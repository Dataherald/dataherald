import logging
import os
import re
import time
from typing import Any

from bson.objectid import ObjectId
from langchain.chains import LLMChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from overrides import override
from sql_metadata import Parser

from dataherald.config import System
from dataherald.db import DB
from dataherald.db_scanner.models.types import TableDescriptionStatus
from dataherald.db_scanner.repository.base import TableDescriptionRepository
from dataherald.eval import Evaluation, Evaluator
from dataherald.sql_database.base import SQLDatabase
from dataherald.sql_database.models.types import DatabaseConnection
from dataherald.types import Question, Response

logger = logging.getLogger(__name__)

SYSTEM_TEMPLATE = """You are a {dialect} expert.
Given a question, a SQL query, and the database schema, analyze the correctness of the SQL query and provide a score.
Score indicates how correctly and accurately SQL query answers the question.
Note that the score should be between 0 and 100. Higher scores means the SQL Query is more accurate.
Double check the SQL query for the common mistakes, including:
- For columns that can contain NULL values, NULL values should be filtered out by using the IS NOT NULL operator in the WHERE condition
- when intention of the question is to include all rows from both sets, including duplicates, using UNION ALL is better than UNION
- BETWEEN is inclusive, if the intention is to exclude the endpoints of the range, use comparison operators (< and >)
- Conditions in the WHERE clause should not have any DATA TYPE mismatch problem
- columns names which contain Spaces, non-alphanumeric character, Reserved keywords or special characters should be inside backticks (``)
- Using the correct number of arguments for functions
- Casting to the correct data type
- Using the proper columns for joins
- using the correct set operators for nested queries
- columns in the SELECT clause should correspond to what exactly asked by user in the question
- check for the improper use of the aggergation functions (SUM, AVG, MIN, MAX, ...)
- robustness of the SQL query in handling cases where data values can be in different format (WHERE lower(column) = lower(entity))
"""

HUMAN_TEMPLATE = """
Give me a score for the SQL query.
Schema of the tables:
{schema}
Here is the question:
Question: {question}
Evaluate the following SQL query:
SQL Query: {SQL}
SQL Query Result: {SQL_result}
give me a one or two lines explanation and the score after 'Score: '.
"""


class SimpleEvaluator(Evaluator):
    llm: Any = None

    def __init__(self, system: System):
        super().__init__(system)
        self.system = system

    def answer_parser(self, answer: str) -> int:
        """
        Extract the number after the Score:
        If not found extract the last number between 0 and 100
        If not found return 0
        """
        pattern = r".*Score:\s*(\d+)"
        match = re.search(pattern, answer)
        output = 0
        if match:
            output = int(match.group(1))
        else:
            pattern = r"\b([0-9]{1,2}|100)\b"
            numbers = re.findall(pattern, answer)
            if numbers:
                output = int(numbers[-1])
        return output

    @override
    def evaluate(
        self,
        question: Question,
        generated_answer: Response,
        database_connection: DatabaseConnection,
    ) -> Evaluation:
        database = SQLDatabase.get_sql_engine(database_connection)
        logger.info(
            f"(Simple evaluator) Generating score for the question/sql pair: {str(question.question)}/ {str(generated_answer.sql_query)}"
        )
        storage = self.system.instance(DB)
        repository = TableDescriptionRepository(storage)
        db_scan = repository.get_all_tables_by_db(
            {
                "db_connection_id": ObjectId(database_connection.id),
                "status": TableDescriptionStatus.SYNCHRONIZED.value,
            }
        )
        self.llm = self.model.get_model(
            database_connection=database_connection,
            temperature=0,
            model_name=os.getenv("LLM_MODEL", "gpt-4"),
        )
        start_time = time.time()
        system_message_prompt = SystemMessagePromptTemplate.from_template(
            SYSTEM_TEMPLATE
        )
        human_message_prompt = HumanMessagePromptTemplate.from_template(HUMAN_TEMPLATE)
        chat_prompt = ChatPromptTemplate.from_messages(
            [system_message_prompt, human_message_prompt]
        )
        user_question = question.question
        sql = generated_answer.sql_query
        dialect = database.dialect
        tables = Parser(sql).tables
        schema = ""
        for scanned_table in db_scan:
            if scanned_table.table_name in tables:
                schema += f"Table: {scanned_table.table_schema}\n"
        if generated_answer.sql_query_result is None:
            logger.info(
                f"(Simple evaluator) SQL query: {sql} is not valid. Returning score 0"
            )
            return Evaluation(
                question_id=question.id, answer_id=generated_answer.id, score=0
            )
        chain = LLMChain(llm=self.llm, prompt=chat_prompt)
        answer = chain.run(
            {
                "dialect": dialect,
                "question": user_question,
                "SQL": sql,
                "SQL_result": str(generated_answer.sql_query_result.json()),
                "schema": schema,
            }
        )
        logger.info(f"(Simple evaluator) answer of the evaluator: {answer}")
        score = self.answer_parser(answer=answer) / 100
        logger.info(f"(Simple evaluator) score of the evaluator: {str(score)}")
        end_time = time.time()
        logger.info(f"Evaluation time elapsed: {str(end_time - start_time)}")
        return Evaluation(
            question_id=question.id, answer_id=generated_answer.id, score=score
        )
