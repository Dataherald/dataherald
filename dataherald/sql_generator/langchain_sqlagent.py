"""A wrapper for the SQL generation functions in langchain"""

import datetime
import logging
import os
import time
from typing import Any, List

from langchain.agents import initialize_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.agents.agent_types import AgentType
from langchain.callbacks import get_openai_callback
from langchain.schema import AgentAction
from overrides import override

from dataherald.sql_database.base import SQLDatabase
from dataherald.sql_database.models.types import DatabaseConnection
from dataherald.sql_generator import SQLGenerator
from dataherald.types import Prompt, SQLGeneration

logger = logging.getLogger(__name__)


class LangChainSQLAgentSQLGenerator(SQLGenerator):
    llm: Any | None = None

    @override
    def generate_response(
        self,
        user_prompt: Prompt,
        database_connection: DatabaseConnection,
        context: List[dict] = None,
    ) -> SQLGeneration:  # type: ignore
        logger.info(f"Generating SQL response to question: {str(user_prompt.dict())}")
        response = SQLGeneration(
            prompt_id=user_prompt.id, created_at=datetime.datetime.now()
        )
        self.llm = self.model.get_model(
            database_connection=database_connection,
            temperature=0,
            model_name=os.getenv("LLM_MODEL", "gpt-4-1106-preview"),
        )
        self.database = SQLDatabase.get_sql_engine(database_connection)
        tools = SQLDatabaseToolkit(db=self.database, llm=self.llm).get_tools()
        start_time = time.time()
        # builds a sql agent using initialize_agent instead of create_sql_agent to get intermediate steps in output
        # to create custom agent: https://python.langchain.com/docs/modules/agents/how_to/custom_llm_chat_agent
        agent_executor = initialize_agent(
            tools,
            self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            handle_parsing_errors=True,
            return_intermediate_steps=True,
        )
        if context is not None:
            samples_prompt_string = "The following are some similar previous questions and their correct SQL queries from these databases: \
            \n"
            for sample in context:
                samples_prompt_string += (
                    f"Question: {sample['prompt_text']} \nSQL: {sample['sql']} \n"
                )

        question_with_context = (
            f"{user_prompt.text} An example of a similar question and the query that was generated \
                                to answer it is the following {samples_prompt_string}"
            if context is not None
            else user_prompt.text
        )
        with get_openai_callback() as cb:
            result = agent_executor(question_with_context)
        sql_query_list = []
        for step in result["intermediate_steps"]:
            action = step[0]
            if type(action) == AgentAction and action.tool == "sql_db_query":
                sql_query_list.append(self.format_sql_query(action.tool_input))
        exec_time = time.time() - start_time
        logger.info(
            f"cost: {str(cb.total_cost)} tokens: {str(cb.total_tokens)} time: {str(exec_time)}"
        )
        response.sql = (sql_query_list[-1] if len(sql_query_list) > 0 else "",)
        response.tokens_used = cb.total_tokens
        response.completed_at = datetime.datetime.now()
        return self.create_sql_query_status(
            self.database,
            response.sql,
            response,
        )
