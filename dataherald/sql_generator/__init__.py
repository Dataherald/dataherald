"""Base class that all sql generation classes inherit from."""
import re
from abc import ABC, abstractmethod
from datetime import date, datetime
from typing import Any, List, Tuple

import sqlparse
from langchain.schema import AgentAction

from dataherald.config import Component, System
from dataherald.model.chat_model import ChatModel
from dataherald.sql_database.base import SQLDatabase
from dataherald.sql_database.models.types import DatabaseConnection
from dataherald.sql_generator.create_sql_query_status import create_sql_query_status
from dataherald.types import Question, Response, SQLQueryResult
from dataherald.utils.strings import contains_line_breaks


class EngineTimeOutORItemLimitError(Exception):
    pass


class SQLGenerator(Component, ABC):
    metadata: Any
    llm: ChatModel | None = None

    def __init__(self, system: System):  # noqa: ARG002
        self.system = system
        self.model = ChatModel(self.system)

    def check_for_time_out_or_tool_limit(self, response: dict) -> dict:
        if (
            response.get("output")
            == "Agent stopped due to iteration limit or time limit."
        ):
            raise EngineTimeOutORItemLimitError(
                "The engine has timed out or reached the tool limit."
            )
        return response

    def create_sql_query_status(
        self,
        db: SQLDatabase,
        query: str,
        response: Response,
        top_k: int = None,
        generate_csv: bool = False,
        database_connection: DatabaseConnection | None = None,
    ) -> Response:
        return create_sql_query_status(
            db,
            query,
            response,
            top_k,
            generate_csv,
            database_connection=database_connection,
        )

    def format_intermediate_representations(
        self, intermediate_representation: List[Tuple[AgentAction, str]]
    ) -> List[str]:
        """Formats the intermediate representation into a string."""
        formatted_intermediate_representation = []
        for item in intermediate_representation:
            formatted_intermediate_representation.append(
                f"Thought: '{str(item[0].log).split('Action:')[0]}'\n"
                f"Action: '{item[0].tool}'\n"
                f"Action Input: '{item[0].tool_input}'\n"
                f"Observation: '{item[1]}'"
            )
        return formatted_intermediate_representation

    def format_sql_query(self, sql_query: str) -> str:
        comments = [
            match.group() for match in re.finditer(r"--.*$", sql_query, re.MULTILINE)
        ]
        sql_query_without_comments = re.sub(r"--.*$", "", sql_query, flags=re.MULTILINE)

        if contains_line_breaks(sql_query_without_comments.strip()):
            return sql_query

        parsed = sqlparse.format(sql_query_without_comments, reindent=True)

        return parsed + "\n" + "\n".join(comments)

    @abstractmethod
    def generate_response(
        self,
        user_question: Question,
        database_connection: DatabaseConnection,
        context: List[dict] = None,
        generate_csv: bool = False,
    ) -> Response:
        """Generates a response to a user question."""
        pass
