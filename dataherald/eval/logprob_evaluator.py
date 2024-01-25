import logging
import math
import os
from typing import Any

import tiktoken
from langchain.callbacks.base import BaseCallbackManager
from langchain.chains import LLMChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from overrides import override

from dataherald.config import System
from dataherald.context_store import ContextStore
from dataherald.db import DB
from dataherald.db_scanner.models.types import TableDescriptionStatus
from dataherald.db_scanner.repository.base import TableDescriptionRepository
from dataherald.eval import Evaluation, Evaluator
from dataherald.sql_database.base import SQLDatabase
from dataherald.sql_database.models.types import DatabaseConnection
from dataherald.sql_generator.log_probs_callback_handler import OpenAILogProbsCallbackHandler
from dataherald.types import Prompt, SQLGeneration

logger = logging.getLogger(__name__)

SYSTEM_TEMPLATE = """You are a {dialect} database administrator.
Your job is to evaluate the correctness of the SQL query given the question and the database schema.
Your job is to return a label which can have two values: 'True' or 'False'.
Respond with just one word, False or True. You must output the word True, or the word False, nothing else.
"""

HUMAN_TEMPLATE = """
Schema of the tables:
{schema}
###
Instructions that SQL query must follow:
Admin Instructions: {admin_instructions}
###
Here is the question:
Question: {question}
###
Evaluate the following SQL query:
SQL Query: {SQL}
SQL Query Result: {SQL_result}
###
"""
MAX_ROWS = 25



class LogProbEvaluator(Evaluator):
    encoder = Any

    def __init__(self, system: System):
        super().__init__(system)
        self.system = system
        self.encoder = tiktoken.get_encoding("cl100k_base")

    @override
    def evaluate(
        self,
        user_prompt: Prompt,
        sql_generation: SQLGeneration,
        database_connection: DatabaseConnection,
    ) -> Evaluation:
        database = SQLDatabase.get_sql_engine(database_connection)
        logger.info(
            f"(logprob evaluator) Evaluating SQL generation {sql_generation.sql}"
        )
        storage = self.system.instance(DB)
        repository = TableDescriptionRepository(storage)
        db_scan = repository.get_all_tables_by_db(
            {
                "db_connection_id": str(database_connection.id),
                "status": TableDescriptionStatus.SCANNED.value,
            }
        )
        callback = OpenAILogProbsCallbackHandler()
        self.llm = self.model.get_model(
            database_connection=database_connection,
            temperature=0,
            callbacks=BaseCallbackManager([callback]),
            logprobs=True,
            model_name=os.getenv("LLM_MODEL", "gpt-4"),
        )
        query = sql_generation.sql
        question = user_prompt.text
        dialect = database.dialect
        system_message_prompt = SystemMessagePromptTemplate.from_template(
            SYSTEM_TEMPLATE
        )
        human_message_prompt = HumanMessagePromptTemplate.from_template(HUMAN_TEMPLATE)
        chat_prompt = ChatPromptTemplate.from_messages(
            [system_message_prompt, human_message_prompt]
        )
        score = 0
        schema = ""
        for scanned_table in db_scan:
            schema += f"Table: {scanned_table.table_schema}\n"
        if sql_generation.status == "INVALID":
            logger.info(
                f"(Simple evaluator) SQL query: {query} is not valid. Returning score 0"
            )
            return Evaluation(
                question_id=user_prompt.id, answer_id=sql_generation.id, score=0
            )
        chain = LLMChain(llm=self.llm, prompt=chat_prompt)
        sql_results = database.run_sql(query, MAX_ROWS)[0]
        context_store = self.system.instance(ContextStore)
        _, db_instructions = context_store.retrieve_context_for_question(
            user_prompt, number_of_samples=1
        )
        admin_instructions = ""
        if db_instructions:
            for index, instruction in enumerate(db_instructions):
                admin_instructions += f"{index+1}) {instruction['instruction']}\n"
        chain.run(
            {
                "dialect": dialect,
                "question": question,
                "SQL": query,
                "admin_instructions": admin_instructions,
                "SQL_result": sql_results,
                "schema": schema,
            }
        )
        for token,log_prob in zip(callback.tokens[0],callback.logprobs[0], strict=False):
            if token == "True":  # noqa: S105
                score = math.exp(log_prob)
            elif token == "False":  # noqa: S105
                score = 1 - math.exp(log_prob)
        return Evaluation(
            question_id=user_prompt.id, answer_id=sql_generation.id, score=score
        )
