import logging

from overrides import override

from dataherald.config import System
from dataherald.eval import Evaluation, Evaluator
from dataherald.sql_database.models.types import DatabaseConnection
from dataherald.types import Prompt, SQLGeneration

logger = logging.getLogger(__name__)
MAX_QUANTILE = 100


class LogProbEvaluator(Evaluator):
    def __init__(self, system: System):
        super().__init__(system)
        self.system = system

    def extract_query_probs(self, tokens, probs):
        """Extract the probabilities for each token in the query."""
        query_probs = []
        query_found = False
        for token, prob in zip(tokens, probs, strict=False):
            if "```" in token or "`" in token:
                query_found = True
            if query_found:
                query_probs.append((token, prob))
        return query_probs

    @override
    def evaluate(
        self,
        user_prompt: Prompt,
        sql_generation: SQLGeneration,
        database_connection: DatabaseConnection,  # noqa: ARG002
    ) -> Evaluation:
        logger.info(
            f"(LogProb evaluator) Generating score for the question/sql pair: {str(user_prompt.text)}/ {str(sql_generation.sql)}"
        )
        if sql_generation.status == "INVALID":
            logger.info(
                f"(LogProb evaluator) SQL query: {sql_generation.sql} is not valid. Returning score 0"
            )
            return Evaluation(
                question_id=user_prompt.id, answer_id=sql_generation.id, score=0.0
            )
        for i in range(len(sql_generation.tokens) - 1, -1, -1):
            query_probs = self.extract_query_probs(
                sql_generation.tokens[i], sql_generation.probs[i]
            )
            if query_probs:
                break
        if not query_probs:
            return Evaluation(
                question_id=user_prompt.id, answer_id=sql_generation.id, score=0.0
            )
        probabilities = sorted([prob for token, prob in query_probs])
        tokens = [token for token, prob in query_probs]
        logger.info(
            f"(LogProb evaluator) Found {len(query_probs)} query tokens {tokens} in {i} step with probabilities."
        )
        total_probs = len(probabilities)
        if sql_generation.evaluation_quantile > MAX_QUANTILE:
            raise ValueError(
                f"Evaluation quantile should be between 0 and 100. Got {sql_generation.evaluation_quantile}"
            )
        index = int(
            round(((sql_generation.evaluation_quantile / 100) * (total_probs - 1)), 0)
        )
        return Evaluation(
            question_id=user_prompt.id,
            answer_id=sql_generation.id,
            score=probabilities[index],
        )
