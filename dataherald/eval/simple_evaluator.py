import logging
import re
import time
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from langchain.chains import LLMChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
)
from overrides import override
from sql_metadata import Parser
from sqlalchemy import text

from dataherald.config import System
from dataherald.db import DB
from dataherald.db_scanner.models.types import TableDescriptionStatus
from dataherald.db_scanner.repository.base import TableDescriptionRepository
from dataherald.eval import Evaluation, Evaluator
from dataherald.sql_database.base import SQLDatabase, SQLInjectionError
from dataherald.sql_database.models.types import DatabaseConnection
from dataherald.types import Prompt, SQLGeneration

logger = logging.getLogger(__name__)


HUMAN_TEMPLATE = """
You are a {dialect} expert.
Given a question, a SQL query, and the database schema, analyze the correctness of the SQL query and provide a score.
Score indicates how correctly and accurately SQL query answers the question.
Note that the score should be between 0 and {MAX_CONFIDENCE}. Higher scores means the SQL Query is more accurate.
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
- all of the dbs are case insensitive, so do not reduce the score based on case sensitivity.
- Using `current_date()` or `current_datetime()` in SQL queries is banned, SQL queries should use exact time in order to return the same results when executed at different times.
For each of the detected mistakes, decrease the score by 10 points.
Give me a score for the SQL query.
Schema of the tables:
{schema}
Here is the question:
Question: {question}
Evaluate the following SQL query:
SQL Query: {SQL}
SQL Query Result: {SQL_result}
give me a one or two lines explanation and the score after 'Score: '.
"""  # noqa: E501
TOP_K = 100


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

    def create_sql_results(self, result: Any) -> list:
        rows = []
        if result:
            for row in result:
                modified_row = {}
                for key, value in zip(row.keys(), row, strict=True):
                    if type(value) in [
                        date,
                        datetime,
                    ]:  # Check if the value is an instance of datetime.date
                        modified_row[key] = str(value)
                    elif (
                        type(value) is Decimal
                    ):  # Check if the value is an instance of decimal.Decimal
                        modified_row[key] = float(value)
                    else:
                        modified_row[key] = value
            rows.append(modified_row)
        return rows

    @override
    def evaluate(
        self,
        user_prompt: Prompt,
        sql_generation: SQLGeneration,
        database_connection: DatabaseConnection,
    ) -> Evaluation:
        max_confidence = 100
        database = SQLDatabase.get_sql_engine(database_connection)
        logger.info(
            f"(Simple evaluator) Generating score for the question/sql pair: {str(user_prompt.text)}/ {str(sql_generation.sql)}"
        )
        storage = self.system.instance(DB)
        repository = TableDescriptionRepository(storage)
        db_scan = repository.get_all_tables_by_db(
            {
                "db_connection_id": str(database_connection.id),
                "status": TableDescriptionStatus.SCANNED.value,
            }
        )
        self.llm = self.model.get_model(
            database_connection=database_connection,
            temperature=0,
            model_name=self.llm_config.llm_name,
            api_base=self.llm_config.api_base,
        )
        start_time = time.time()
        human_message_prompt = HumanMessagePromptTemplate.from_template(HUMAN_TEMPLATE)
        chat_prompt = ChatPromptTemplate.from_messages([human_message_prompt])
        user_question = user_prompt.text
        sql = sql_generation.sql
        dialect = database.dialect
        try:
            tables = Parser(sql).tables
        except Exception as e:
            logger.info(
                f"(Simple evaluator) error while parsing the SQL query: {str(e)}. Returning score 0"
            )
            return Evaluation(
                question_id=user_prompt.id, answer_id=sql_generation.id, score=0
            )
        schema = ""
        for scanned_table in db_scan:
            if scanned_table.table_name in tables:
                schema += f"Table: {scanned_table.table_schema}\n"
        if sql_generation.status == "INVALID":
            logger.info(
                f"(Simple evaluator) SQL query: {sql} is not valid. Returning score 0"
            )
            return Evaluation(
                question_id=user_prompt.id, answer_id=sql_generation.id, score=0
            )
        chain = LLMChain(llm=self.llm, prompt=chat_prompt)
        try:
            query = database.parser_to_filter_commands(sql_generation.sql)
            with database._engine.connect() as connection:
                execution = connection.execute(text(query))
                result = execution.fetchmany(TOP_K)
            rows = self.create_sql_results(result)

        except SQLInjectionError as e:
            raise SQLInjectionError(
                "Sensitive SQL keyword detected in the query."
            ) from e
        if not rows:
            logger.info(
                f"(Simple evaluator) SQL query: {sql} returned no results. max confidence is 70"
            )
            max_confidence = 70
        answer = chain.invoke(
            {
                "dialect": dialect,
                "question": user_question,
                "SQL": sql,
                "SQL_result": "\n".join([str(row) for row in rows]),
                "MAX_CONFIDENCE": str(max_confidence),
                "schema": schema,
            }
        )["text"]
        logger.info(f"(Simple evaluator) answer of the evaluator: {answer}")
        score = self.answer_parser(answer=answer) / 100
        logger.info(f"(Simple evaluator) score of the evaluator: {str(score)}")
        end_time = time.time()
        logger.info(f"Evaluation time elapsed: {str(end_time - start_time)}")
        return Evaluation(
            question_id=user_prompt.id, answer_id=sql_generation.id, score=score
        )
