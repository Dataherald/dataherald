"""Base class that all sql generation classes inherit from."""
from abc import ABC, abstractmethod
from dataherald.config import Component, System
from typing import Any, Optional, Dict
from dataherald.sql_database.base import SQLDatabase
from dataherald.config import Component
from langchain.base_language import BaseLanguageModel
from langchain.chat_models import ChatOpenAI


class SQLGenerator(Component, ABC):
    database: SQLDatabase
    metadata: Any
    llm: Optional[BaseLanguageModel] = None

    def __init__(self, sytstem: System):
        llm = ChatOpenAI(temperature=0, openai_api_key='', model_name='gpt-3.5-turbo')
        pass

    @abstractmethod
    def generate_response(self, user_question:str) -> str:
        """Generates a response to a user question."""
        pass
    
    

