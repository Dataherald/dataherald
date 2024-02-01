"""Base class that all sql generation classes inherit from."""
import os
import re
from abc import ABC, abstractmethod
from typing import Any, List, Tuple

import sqlparse
from langchain.schema import AgentAction

from dataherald.config import Component, System
from dataherald.model.chat_model import ChatModel
from dataherald.sql_database.base import SQLDatabase
from dataherald.sql_database.models.types import DatabaseConnection
from dataherald.sql_generator.create_sql_query_status import create_sql_query_status
from dataherald.types import LLMConfig, Prompt, SQLGeneration
from dataherald.utils.strings import contains_line_breaks


class EngineTimeOutORItemLimitError(Exception):
    pass


class SQLGenerator(Component, ABC):
    metadata: Any
    llm: ChatModel | None = None

    def __init__(self, system: System, llm_config: LLMConfig):  # noqa: ARG002
        self.system = system
        self.llm_config = llm_config
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

    def remove_markdown(self, query: str) -> str:
        pattern = r"```sql(.*?)```"
        matches = re.findall(pattern, query, re.DOTALL)
        if matches:
            return matches[0].strip()
        return ""

    @classmethod
    def get_upper_bound_limit(cls) -> int:
        top_k = os.getenv("UPPER_LIMIT_QUERY_RETURN_ROWS", None)
        if top_k is None or top_k == "":
            top_k = 50
        return top_k if isinstance(top_k, int) else int(top_k)

    def create_sql_query_status(
        self, db: SQLDatabase, query: str, sql_generation: SQLGeneration
    ) -> SQLGeneration:
        return create_sql_query_status(db, query, sql_generation)

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
        user_prompt: Prompt,
        database_connection: DatabaseConnection,
        context: List[dict] = None,
    ) -> SQLGeneration:
        """Generates a response to a user question."""
        pass
