"""Base class that all sql generation classes inherit from."""

import datetime
import logging
import os
import re
from abc import ABC, abstractmethod
from queue import Queue
from typing import Any, Dict, List, Tuple

import sqlparse
from langchain.agents.agent import AgentExecutor
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import AgentAction, LLMResult
from langchain_community.callbacks import get_openai_callback

from dataherald.config import Component, System
from dataherald.db_scanner.models.types import TableDescription
from dataherald.model.chat_model import ChatModel
from dataherald.repositories.sql_generations import (
    SQLGenerationRepository,
)
from dataherald.sql_database.base import SQLDatabase, SQLInjectionError
from dataherald.sql_database.models.types import DatabaseConnection
from dataherald.sql_generator.create_sql_query_status import create_sql_query_status
from dataherald.types import IntermediateStep, LLMConfig, Prompt, SQLGeneration
from dataherald.utils.strings import contains_line_breaks


class EngineTimeOutORItemLimitError(Exception):
    pass


def replace_unprocessable_characters(text: str) -> str:
    """Replace unprocessable characters with a space."""
    text = text.strip()
    return text.replace(r"\_", "_")


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
        return query

    @staticmethod
    def get_table_schema(table_name: str, db_scan: List[TableDescription]) -> str:
        for table in db_scan:
            if table.table_name == table_name:
                return table.schema_name
        return ""

    @staticmethod
    def filter_tables_by_schema(
        db_scan: List[TableDescription], prompt: Prompt
    ) -> List[TableDescription]:
        if prompt.schemas:
            return [table for table in db_scan if table.schema_name in prompt.schemas]
        return db_scan

    def format_sql_query_intermediate_steps(self, step: str) -> str:
        pattern = r"```sql(.*?)```"

        def formatter(match):
            original_sql = match.group(1)
            formatted_sql = self.format_sql_query(original_sql)
            return "```sql\n" + formatted_sql + "\n```"

        return re.sub(pattern, formatter, step, flags=re.DOTALL)

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

    def format_sql_query(self, sql_query: str) -> str:
        comments = [
            match.group() for match in re.finditer(r"--.*$", sql_query, re.MULTILINE)
        ]
        sql_query_without_comments = re.sub(r"--.*$", "", sql_query, flags=re.MULTILINE)

        if contains_line_breaks(sql_query_without_comments.strip()):
            return sql_query

        parsed = sqlparse.format(sql_query_without_comments, reindent=True)

        return parsed + "\n" + "\n".join(comments)

    def extract_query_from_intermediate_steps(
        self, intermediate_steps: List[Tuple[AgentAction, str]]
    ) -> str:
        """Extract the SQL query from the intermediate steps."""
        sql_query = ""
        for step in intermediate_steps:
            action = step[0]
            if type(action) == AgentAction and action.tool == "SqlDbQuery":
                if "SELECT" in self.format_sql_query(action.tool_input).upper():
                    sql_query = self.remove_markdown(action.tool_input)
        if sql_query == "":
            for step in intermediate_steps:
                thought = str(step[0].log).split("Action:")[0]
                if "```sql" in thought:
                    sql_query = self.remove_markdown(thought)
                    if not sql_query.upper().strip().startswith("SELECT"):
                        sql_query = ""
        return sql_query

    def construct_intermediate_steps(
        self, intermediate_steps: List[Tuple[AgentAction, str]], suffix: str = ""
    ) -> List[IntermediateStep]:
        """Constructs the intermediate steps."""
        formatted_intermediate_steps = []
        for step in intermediate_steps:
            if step[0].tool == "SqlDbQuery":
                formatted_intermediate_steps.append(
                    IntermediateStep(
                        thought=str(step[0].log).split("Action:")[0],
                        action=step[0].tool,
                        action_input=step[0].tool_input,
                        observation="QUERY RESULTS ARE NOT STORED FOR PRIVACY REASONS.",
                    )
                )
            else:
                formatted_intermediate_steps.append(
                    IntermediateStep(
                        thought=str(step[0].log).split("Action:")[0],
                        action=step[0].tool,
                        action_input=step[0].tool_input,
                        observation=self.truncate_observations(step[1]),
                    )
                )
        formatted_intermediate_steps[0].thought = suffix.split("Thought: ")[1].split(
            "{agent_scratchpad}"
        )[0]
        return formatted_intermediate_steps

    def truncate_observations(self, obervarion: str, max_length: int = 2000) -> str:
        """Truncate the tool input."""
        return (
            obervarion[:max_length] + "... (truncated)"
            if len(obervarion) > max_length
            else obervarion
        )

    @abstractmethod
    def generate_response(
        self,
        user_prompt: Prompt,
        database_connection: DatabaseConnection,
        context: List[dict] = None,
        metadata: dict = None,
    ) -> SQLGeneration:
        """Generates a response to a user question."""
        pass

    def stream_agent_steps(  # noqa: PLR0912, C901
        self,
        question: str,
        agent_executor: AgentExecutor,
        response: SQLGeneration,
        sql_generation_repository: SQLGenerationRepository,
        queue: Queue,
        metadata: dict = None,
    ):  # noqa: PLR0912
        try:
            with get_openai_callback() as cb:
                for chunk in agent_executor.stream(
                    {"input": question}, {"metadata": metadata}
                ):
                    if "actions" in chunk:
                        for message in chunk["messages"]:
                            queue.put(
                                self.format_sql_query_intermediate_steps(
                                    message.content
                                )
                                + "\n"
                            )
                    elif "steps" in chunk:
                        for step in chunk["steps"]:
                            queue.put(
                                f"\n**Observation:**\n {self.format_sql_query_intermediate_steps(step.observation)}\n"
                            )
                    elif "output" in chunk:
                        queue.put(
                            f'\n**Final Answer:**\n {self.format_sql_query_intermediate_steps(chunk["output"])}'
                        )
                        if "```sql" in chunk["output"]:
                            response.sql = replace_unprocessable_characters(
                                self.remove_markdown(chunk["output"])
                            )
                    else:
                        raise ValueError()
        except SQLInjectionError as e:
            raise SQLInjectionError(e) from e
        except EngineTimeOutORItemLimitError as e:
            raise EngineTimeOutORItemLimitError(e) from e
        except Exception as e:
            response.sql = ("",)
            response.status = ("INVALID",)
            response.error = (str(e),)
        finally:
            queue.put(None)
            response.tokens_used = cb.total_tokens
            response.completed_at = datetime.datetime.now()
            if not response.error:
                if response.sql:
                    response = self.create_sql_query_status(
                        self.database,
                        response.sql,
                        response,
                    )
                else:
                    response.status = "INVALID"
                    response.error = "No SQL query generated"
            sql_generation_repository.update(response)

    @abstractmethod
    def stream_response(
        self,
        user_prompt: Prompt,
        database_connection: DatabaseConnection,
        response: SQLGeneration,
        queue: Queue,
        metadata: dict = None,
    ):
        """Streams a response to a user question."""
        pass
