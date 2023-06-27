from dataherald.api import API
from dataherald.config import System
import requests
import time
from overrides import override
from dataherald.smart_cache import SmartCache
from dataherald.eval import Evaluator
from dataherald.sql_generator import SQLGenerator 
from dataherald.eval.simple_evaluator import Evaluator
from dataherald.types import NLQuery, NLQueryResponse
import uuid
from fastapi.encoders import jsonable_encoder

class FastAPI(API):
    def __init__(self, system: System):
        super().__init__(system)
        self.system = system
        url_prefix = "https" if system.settings.dh_server_ssl_enabled else "http"
        system.settings.require("dh_server_host")
        system.settings.require("dh_server_http_port")
        self._api_url = f"{url_prefix}://{system.settings.dh_server_host}:{system.settings.dh_server_http_port}/api/v1"

    @override
    def heartbeat(self) -> int:
        """Returns the current server time in nanoseconds to check if the server is alive"""
        return int(time.time_ns())
    
    
    def answer_question(self, question: str) -> NLQueryResponse:
        """Takes in an English question and answers it based on content from the registered databases"""
        cache = self.system.instance(SmartCache)
        sql_generation = self.system.instance(SQLGenerator)
        evaluator = self.system.instance(Evaluator)

        user_question = NLQuery(question=question, id=uuid.uuid4())

        generated_answer = cache.lookup(user_question.question)
        if generated_answer is None:
            generated_answer = sql_generation.generate_response(user_question)
            if evaluator.evaluate(generated_answer):
                cache.add(question, generated_answer)
            
        else:
            print('cache hit')    

        response = jsonable_encoder(generated_answer)
        print(response)
        return response
    
    def connect_database(self, question: str) -> str:
        """Takes in an English question and answers it based on content from the registered databases"""
        return "I can't do that yet"
    
    def add_context(self, question: str) -> str:
        """Takes in an English question and answers it based on content from the registered databases"""
        return "I can't do that yet"
