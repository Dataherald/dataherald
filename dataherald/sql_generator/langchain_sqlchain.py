"""A wrapper for the SQL generation functions in langchain"""

import datetime
import logging
import os
from typing import Any, List

from langchain import SQLDatabaseChain
from langchain.callbacks import get_openai_callback
from overrides import override

from dataherald.sql_database.base import SQLDatabase
from dataherald.sql_database.models.types import DatabaseConnection
from dataherald.sql_generator import SQLGenerator
from dataherald.types import Prompt, SQLGeneration

logger = logging.getLogger(__name__)

PROMPT_WITHOUT_CONTEXT = """
Given an input question,
first create a syntactically correct postgresql query to run,
then look at the results of the query and return the answer.

The question:
{user_question}
"""

PROMPT_WITH_CONTEXT = """
Given an input question,
first create a syntactically correct postgresql query to run,
then look at the results of the query and return the answer.

An example of a similar question and the query that was generated to answer it is the following
{context}

The question:
{user_question}
"""


class LangChainSQLChainSQLGenerator(SQLGenerator):
    llm: Any | None = None

    @override
    def generate_response(
        self,
        user_prompt: Prompt,
        database_connection: DatabaseConnection,
        context: List[dict] = None,
    ) -> SQLGeneration:
        response = SQLGeneration(
            prompt_id=user_prompt.id,
            created_at=datetime.datetime.now(),
        )
        self.llm = self.model.get_model(
            database_connection=database_connection,
            temperature=0,
            model_name=os.getenv("LLM_MODEL", "gpt-4-1106-preview"),
        )
        self.database = SQLDatabase.get_sql_engine(database_connection)
        logger.info(
            f"Generating SQL response to question: {str(user_prompt.dict())} with passed context {context}"
        )
        if context is not None:
            samples_prompt_string = "The following are some similar previous questions and their correct SQL queries from these databases: \
            \n"
            for sample in context:
                samples_prompt_string += (
                    f"Question: {sample['prompt_text']} \nSQL: {sample['sql']} \n"
                )

            prompt = PROMPT_WITH_CONTEXT.format(
                user_question=user_prompt.text, context=samples_prompt_string
            )
        else:
            prompt = PROMPT_WITHOUT_CONTEXT.format(user_question=user_prompt.text)
        # should top_k be an argument?
        db_chain = SQLDatabaseChain.from_llm(
            self.llm, self.database, top_k=3, return_intermediate_steps=True
        )
        with get_openai_callback() as cb:
            result = db_chain(prompt)
        logger.info(f"cost: {str(cb.total_cost)} tokens: {str(cb.total_tokens)}")
        response.tokens_used = cb.total_tokens
        response.sql = self.format_sql_query(result["intermediate_steps"][1])
        response.completed_at = datetime.datetime.now()
        return self.create_sql_query_status(
            self.database,
            response.sql,
            response,
        )
