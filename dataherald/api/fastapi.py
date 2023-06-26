from dataherald.api import API
from dataherald.config import System
import requests
import time
from overrides import override
from dataherald.smart_cache.in_memory import InMemoryCache
from dataherald.eval.simple_evaluator import SimpleEvaluator
from dataherald.sql_generation.langchain_sql import LangChainSQLGenerator 
from dataherald.eval.simple_evaluator import SimpleEvaluator

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
    
    
    def answer_question(self, question) -> str:
        """Takes in an English question and answers it based on content from the registered databases"""
        cache = self.system.instance(InMemoryCache)
        sql_generation = self.system.instance(LangChainSQLGenerator)
        evaluator = self.system.instance(SimpleEvaluator)

        generated_answer = cache.lookup(question)

        if generated_answer is None:
            generated_answer = sql_generation.generate_response(question)
            if evaluator.evaluate(generated_answer):
                cache.add(question, generated_answer)
            
        else:
            print('cache hit')    

        return generated_answer
    
    def connect_database(self, question) -> str:
        """Takes in an English question and answers it based on content from the registered databases"""
        return "I can't do that yet"
    
    def add_context(self, question) -> str:
        """Takes in an English question and answers it based on content from the registered databases"""
        return "I can't do that yet"
