"""Base class that all sql generation classes inherit from."""
import re
from abc import ABC, abstractmethod
from datetime import date, datetime
from typing import Any, List

from langchain.base_language import BaseLanguageModel

from dataherald.config import Component, System
from dataherald.model.chat_model import ChatModel
from dataherald.sql_database.base import SQLDatabase
from dataherald.sql_database.models.types import DatabaseConnection
from dataherald.sql_generator.create_sql_query_status import create_sql_query_status
from dataherald.types import NLQuery, NLQueryResponse, SQLQueryResult


class SQLGenerator(Component, ABC):
    metadata: Any
    llm: BaseLanguageModel | None = None

    def __init__(self, system: System):  # noqa: ARG002
        self.system = system
        model = ChatModel(self.system)
        self.llm = model.get_model(temperature=0)

    def create_sql_query_status(
        self, db: SQLDatabase, query: str, response: NLQueryResponse
    ) -> NLQueryResponse:
        return create_sql_query_status(db, query, response)

    @abstractmethod
    def generate_response(
        self,
        user_question: NLQuery,
        database_connection: DatabaseConnection,
        context: List[dict] = None,
    ) -> NLQueryResponse:
        """Generates a response to a user question."""
        pass
