"""A wrapper for the SQL generation functions in langchain"""

from typing import Optional
from dataherald.sql_generator import SQLGenerator
from langchain.chains import SQLDatabaseSequentialChain as LangchainSQLChain
from langchain import LLMChain, OpenAI
from dataherald.types import NLQuery, NLQueryResponse
from overrides import override
import logging

logger = logging.getLogger(__name__)

class LangChainSQLGenerator(SQLGenerator):
    @override
    def generate_response(self, user_question: NLQuery) -> NLQueryResponse:
        logger.info('Generating SQL response to question: ', user_question.dict())
        return NLQueryResponse(nl_question_id=user_question.id,
                                table_response = [],
                                nl_response = 'That Worked!',
                                tables_used = ['redfin_prices'],
                                sql = 'SELECT * FROM redfin_prices')
    



    

   