"""A wrapper for the SQL generation functions in langchain"""

import logging

from overrides import override

from dataherald.sql_generator import SQLGenerator
from dataherald.types import NLQuery, NLQueryResponse

logger = logging.getLogger(__name__)


class LangChainSQLGenerator(SQLGenerator):
    @override
    def generate_response(self, user_question: NLQuery) -> NLQueryResponse:
        logger.info("Generating SQL response to question:\n" + user_question.dict())
        return NLQueryResponse(
            nl_question_id=user_question.id,
            table_response=[],
            nl_response="That Worked!",
            tables_used=["redfin_prices"],
            sql="SELECT * FROM redfin_prices",
        )
