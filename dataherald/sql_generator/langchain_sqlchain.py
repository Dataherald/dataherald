"""A wrapper for the SQL generation functions in langchain"""

import logging

from langchain import SQLDatabaseChain
from overrides import override

from dataherald.sql_generator import SQLGenerator
from dataherald.types import NLQuery, NLQueryResponse

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
    @override
    def generate_response(self, user_question: NLQuery, context: str = None) -> NLQueryResponse:
        logger.info(f"Generating SQL response to question: {str(user_question.dict())}")
        if context is not None:
            prompt = PROMPT_WITH_CONTEXT.format(user_question=user_question.question, context=context)
        else:
            prompt = PROMPT_WITHOUT_CONTEXT.format(user_question=user_question.question)
        # should top_k be an argument?
        db_chain = SQLDatabaseChain.from_llm(
            self.llm, self.database, top_k=3, return_intermediate_steps=True
        )

        result = db_chain(prompt)

        intermediate_steps = []
        for step in result["intermediate_steps"]:
            intermediate_steps.append(str(step))

        return NLQueryResponse(
            nl_question_id=user_question.id,
            nl_response=result["result"],
            intermediate_steps=intermediate_steps,
            sql_query=result["intermediate_steps"][1],
        )
