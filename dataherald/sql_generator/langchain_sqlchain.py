"""A wrapper for the SQL generation functions in langchain"""

import logging

from langchain import SQLDatabaseChain
from overrides import override

from dataherald.sql_generator import SQLGenerator
from dataherald.types import NLQuery, NLQueryResponse

logger = logging.getLogger(__name__)

PROMPT = """
Given an input question,
first create a syntactically correct postgresql query to run,
then look at the results of the query and return the answer.

The question:
{user_question}
"""


class LangChainSQLChainSQLGenerator(SQLGenerator):
    @override
    def generate_response(self, user_question: NLQuery) -> NLQueryResponse:
        logger.info("Generating SQL response to question: " + user_question.dict())

        # needs uri
        db = self.database.from_uri(self.database.uri)

        # should top_k be an argument?
        db_chain = SQLDatabaseChain.from_llm(
            self.llm, db, top_k=3, return_intermediate_steps=True
        )

        result = db_chain(PROMPT.format(user_question=user_question))

        intermediate_steps = []
        for step in result["intermediate_steps"]:
            intermediate_steps.append(str(step))

        return NLQueryResponse(
            nl_question_id=user_question.id,
            nl_response=result["result"],
            intermediate_steps=intermediate_steps,
            sql_query=result["intermediate_steps"][1],
        )
