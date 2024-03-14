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
from langchain.schema.messages import BaseMessage
from langchain_community.callbacks import get_openai_callback

from dataherald.config import Component, System
from dataherald.model.chat_model import ChatModel
from dataherald.repositories.sql_generations import (
    SQLGenerationRepository,
)
from dataherald.sql_database.base import SQLDatabase, SQLInjectionError
from dataherald.sql_database.models.types import DatabaseConnection
from dataherald.sql_generator.create_sql_query_status import create_sql_query_status
from dataherald.types import LLMConfig, Prompt, SQLGeneration
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

    def extract_query_from_intermediate_steps(
        self, intermediate_steps: List[Tuple[AgentAction, str]]
    ) -> str:
        """Extract the SQL query from the intermediate steps."""
        sql_query = ""
        for step in intermediate_steps:
            action = step[0]
            if type(action) == AgentAction and action.tool == "SqlDbQuery":
                sql_query = self.format_sql_query(action.tool_input)
                if "```sql" in sql_query:
                    sql_query = self.remove_markdown(sql_query)
        if sql_query == "":
            for step in intermediate_steps:
                action = step[0]
                sql_query = action.tool_input
                if "```sql" in sql_query:
                    sql_query = self.remove_markdown(sql_query)

        return sql_query

    @abstractmethod
    def generate_response(
        self,
        user_prompt: Prompt,
        database_connection: DatabaseConnection,
        context: List[dict] = None,
    ) -> SQLGeneration:
        """Generates a response to a user question."""
        pass

    def stream_agent_steps(  # noqa: C901
        self,
        question: str,
        agent_executor: AgentExecutor,
        response: SQLGeneration,
        sql_generation_repository: SQLGenerationRepository,
        queue: Queue,
    ):
        try:
            with get_openai_callback() as cb:
                for chunk in agent_executor.stream({"input": question}):
                    if "actions" in chunk:
                        for message in chunk["messages"]:
                            queue.put(message.content + "\n")
                    elif "steps" in chunk:
                        for step in chunk["steps"]:
                            queue.put(f"Observation: `{step.observation}`\n")
                    elif "output" in chunk:
                        queue.put(f'Final Answer: {chunk["output"]}')
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
    ):
        """Streams a response to a user question."""
        pass
