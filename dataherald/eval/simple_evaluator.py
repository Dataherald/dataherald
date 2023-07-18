import logging
import re
import time

from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from overrides import override
from sql_metadata import Parser

from dataherald.config import System
from dataherald.eval import Evaluation, Evaluator
from dataherald.types import NLQuery, NLQueryResponse

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
give me a one or two lines explanation and the score after 'Score: '.
"""


class SimpleEvaluator(Evaluator):
    llm_model_name: str = "gpt-4"

    def __init__(self, system: System):
        super().__init__(system)
        self.system = system
        openai_api_key = system.settings.require("openai_api_key")
        self.llm = ChatOpenAI(
            temperature=0,
            openai_api_key=openai_api_key,
            model_name=self.llm_model_name,
        )

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
        self, question: NLQuery, generated_answer: NLQueryResponse
    ) -> Evaluation:
        logger.info(
            f"(Simple evaluator) Generating score for the question/sql pair: {str(question.question)}/ {str(generated_answer.sql_query)}"
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
        dialect = self.database.dialect
        tables = Parser(sql).tables
        self.database._sample_rows_in_table_info = 0
        schema = self.database.get_table_info_no_throw(tables)
        chain = LLMChain(llm=self.llm, prompt=chat_prompt)
        answer = chain.run(
            {
                "dialect": dialect,
                "question": user_question,
                "SQL": sql,
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
