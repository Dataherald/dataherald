import json
import logging
import time
from typing import List

from bson import json_util
from overrides import override

from dataherald.api import API
from dataherald.config import System
from dataherald.context_store import ContextStore
from dataherald.db import DB
from dataherald.eval import Evaluation, Evaluator
from dataherald.smart_cache import SmartCache
from dataherald.sql_generator import SQLGenerator
from dataherald.types import DataDefinitionType, NLQuery, NLQueryResponse

logger = logging.getLogger(__name__)


class FastAPI(API):
    def __init__(self, system: System):
        super().__init__(system)
        self.system = system

    @override
    def heartbeat(self) -> int:
        """Returns the current server time in nanoseconds to check if the server is alive"""
        return int(time.time_ns())

    @override
    def answer_question(self, question: str) -> NLQueryResponse:
        """Takes in an English question and answers it based on content from the registered databases"""
        cache = self.system.instance(SmartCache)
        sql_generation = self.system.instance(SQLGenerator)
        evaluator = self.system.instance(Evaluator)
        db = self.system.instance(DB)
        context_store = self.system.instance(ContextStore)

        user_question = NLQuery(question=question)
        user_question.id = db.insert_one(
            "nl_question", user_question.dict(exclude={"id"})
        )

        context = context_store.retrieve_context_for_question(question)
        start_generated_answer = time.time()

        generated_answer = cache.lookup(user_question.question)
        if generated_answer is None:
            generated_answer = sql_generation.generate_response(user_question, context)
            if evaluator.is_acceptable_response(user_question, generated_answer):
                cache.add(question, generated_answer)
        generated_answer.exec_time = time.time() - start_generated_answer
        db.insert_one("nl_query_response", generated_answer.dict(exclude={"id"}))
        return json.loads(json_util.dumps(generated_answer))

    @override
    def evaluate_question(self, question: str, golden_sql: str) -> Evaluation:
        """Evaluates an English question within the registered Evaluator"""
        pass

    @override
    def connect_database(self, question: str) -> str:
        """TODO"""
        pass

    def add_data_definition(self, type: DataDefinitionType, uri: str) -> bool:
        """Take in a URI to a document containing data definitions"""
        context_store = self.system.instance(ContextStore)
        return context_store.add_data_definition(type, uri)

    @override
    def add_golden_records(self, golden_records: List) -> bool:
        """Takes in a list of NL <> SQL pairs and stores them to be used in prompts to the LLM"""
        context_store = self.system.instance(ContextStore)
        return context_store.add_golden_records(golden_records)
