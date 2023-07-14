"""Base class that all sql generation classes inherit from."""
import re
from abc import ABC, abstractmethod
from typing import Any

from langchain.base_language import BaseLanguageModel
from langchain.chat_models import ChatOpenAI

from dataherald.config import Component, System

# from dataherald.sql_database.base import SQLDatabase
from dataherald.types import NLQuery, NLQueryResponse


class SQLGenerator(Component, ABC):
    # database: SQLDatabase
    metadata: Any
    llm: BaseLanguageModel | None = None

    def __init__(self, system: System):  # noqa: ARG002
        openai_api_key = system.settings.require("openai_api_key")
        self.llm = ChatOpenAI(
            temperature=0,
            openai_api_key=openai_api_key,
            model_name="gpt-4-32k",
        )

    @abstractmethod
    def generate_response(
        self, user_question: NLQuery, context: str = None
    ) -> NLQueryResponse:
        """Generates a response to a user question."""
        pass
