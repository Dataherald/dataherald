import json
import logging
import time

from bson import json_util
from overrides import override

from dataherald.api import API
from dataherald.config import System
from dataherald.db import DB
from dataherald.eval import Evaluator
from dataherald.smart_cache import SmartCache
from dataherald.sql_generator import SQLGenerator
from dataherald.types import NLQuery, NLQueryResponse

logger = logging.getLogger(__name__)


class FastAPI(API):
    def __init__(self, system: System):
        super().__init__(system)
        self.system = system
        url_prefix = "https" if system.settings.server_ssl_enabled else "http"
        system.settings.require("server_host")
        system.settings.require("server_http_port")
        self._api_url = f"{url_prefix}://{system.settings.server_host}:{system.settings.server_http_port}/api/v1"

    @override
    def heartbeat(self) -> int:
        """Returns the current server time in nanoseconds to check if the server is alive"""
        return int(time.time_ns())

    def answer_question(self, question: str) -> NLQueryResponse:
        """Takes in an English question and answers it based on content from the registered databases"""
        cache = self.system.instance(SmartCache)
        sql_generation = self.system.instance(SQLGenerator)
        evaluator = self.system.instance(Evaluator)
        db = self.system.instance(DB)

        user_question = NLQuery(question=question)
        user_question.id = db.insert_one("nl_question", user_question.dict())

        generated_answer = cache.lookup(user_question.question)
        if generated_answer is None:
            generated_answer = sql_generation.generate_response(user_question)
            if evaluator.evaluate(generated_answer):
                cache.add(question, generated_answer)
        db.insert_one("nl_query_response", generated_answer.dict())
        return json.loads(json_util.dumps(generated_answer))

    def connect_database(self, question: str) -> str:
        """Takes in an English question and answers it based on content from the registered databases"""
        pass

    def add_context(self, question: str) -> str:
        """Takes in an English question and answers it based on content from the registered databases"""
        pass
