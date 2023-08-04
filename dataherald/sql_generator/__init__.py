"""Base class that all sql generation classes inherit from."""
import re
from abc import ABC, abstractmethod
from datetime import date, datetime
from typing import Any, List

from langchain.base_language import BaseLanguageModel
from langchain.chat_models import ChatOpenAI

from dataherald.config import Component, System
from dataherald.sql_database.base import SQLDatabase
from dataherald.sql_database.models.types import DatabaseConnection
from dataherald.types import NLQuery, NLQueryResponse, SQLQueryResult


class SQLGenerator(Component, ABC):
    metadata: Any
    llm: BaseLanguageModel | None = None

    def __init__(self, system: System):  # noqa: ARG002
        self.system = system
        openai_api_key = system.settings.require("openai_api_key")
        self.llm = ChatOpenAI(
            temperature=0,
            openai_api_key=openai_api_key,
            model_name="gpt-4-32k",
        )

    def create_sql_query_status(
        self, db: SQLDatabase, query: str, response: NLQueryResponse
    ) -> NLQueryResponse:
        """Find the sql query status and populate the fields sql_query_result, sql_generation_status, and error_message"""
        if query == "":
            response.sql_generation_status = "NONE"
            response.sql_query_result = None
            response.error_message = None
        else:
            try:
                execution = db.engine.execute(query)
                columns = execution.keys()
                result = execution.fetchall()
                if len(result) == 0:
                    response.sql_query_result = None
                else:
                    columns = [item for item in columns]  # noqa: C416
                    rows = []
                    for row in result:
                        modified_row = {}
                        for key, value in zip(row.keys(), row, strict=True):
                            if (
                                type(value) is date
                            ):  # Check if the value is an instance of datetime.date
                                modified_row[key] = datetime(
                                    value.year, value.month, value.day
                                )
                            else:
                                modified_row[key] = value
                        rows.append(modified_row)
                    response.sql_query_result = SQLQueryResult(
                        columns=columns, rows=rows
                    )
                response.sql_generation_status = "VALID"
                response.error_message = None
            except Exception as e:
                response.sql_generation_status = "INVALID"
                response.sql_query_result = None
                response.error_message = str(e)
        return response

    @abstractmethod
    def generate_response(
        self,
        user_question: NLQuery,
        database_connection: DatabaseConnection,
        context: List[dict] = None,
    ) -> NLQueryResponse:
        """Generates a response to a user question."""
        pass
