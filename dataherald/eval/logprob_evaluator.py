import logging
import math
from typing import Any

import tiktoken
from overrides import override

from dataherald.config import System
from dataherald.eval import Evaluation, Evaluator
from dataherald.sql_database.models.types import DatabaseConnection
from dataherald.types import Prompt, SQLGeneration

logger = logging.getLogger(__name__)


class LogProbEvaluator(Evaluator):
    encoder = Any

    def __init__(self, system: System):
        super().__init__(system)
        self.system = system
        self.encoder = tiktoken.get_encoding("cl100k_base")

    def find_logprobs(self, tokens_list, log_probs_list, query_tokens):
        len_tokens, len_query = len(tokens_list), len(query_tokens)
        for i in range(len_tokens - len_query + 1):
            if tokens_list[i : i + len_query] == tokens_list:
                return log_probs_list[i : i + len_query]
        return None

    @override
    def evaluate(
        self,
        user_prompt: Prompt,
        sql_generation: SQLGeneration,
        database_connection: DatabaseConnection,  # noqa: ARG002
        logprobs: list,  # noqa: ARG002
    ) -> Evaluation:
        query = sql_generation.sql
        query = query + "\n"
        query_tokens = [
            self.encoder.decode_single_token_bytes(token).decode("utf-8")
            for token in self.encoder.encode(query)
        ]
        score = 0
        from ipdb import set_trace; set_trace()
        if "final_answer" == logprobs[-1][0]:
            step_logprobs = logprobs[-1][1]
            tokens_list = [token["token"] for token in step_logprobs]
            log_probs_list = [token["logprob"] for token in step_logprobs]
            log_probs = self.find_logprobs(tokens_list, log_probs_list, query_tokens)
            if log_probs:
                logger.info("query tokens have been found in final answer")
                probs = [math.exp(log_prob) for log_prob in log_probs]
                score = sum(probs) / len(probs)
        if not log_probs:
            for i in range(len(logprobs) - 1, -1, -1):
                if (
                    "execute_query" == logprobs[i][0]
                    or "sql_db_query" == logprobs[i][0]
                ):
                    step_logprobs = logprobs[i][1]
                    tokens_list = [token["token"] for token in step_logprobs]
                    log_probs_list = [token["logprob"] for token in step_logprobs]
                    log_probs = self.find_logprobs(
                        tokens_list, log_probs_list, query_tokens
                    )
                    if log_probs:
                        logger.info("query tokens have been found in execute query")
                        probs = [math.exp(log_prob) for log_prob in log_probs]
                        score = sum(probs) / len(probs)
                        break

        return Evaluation(
            question_id=user_prompt.id, answer_id=sql_generation.id, score=score
        )
