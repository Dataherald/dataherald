"""A wrapper for the SQL generation functions in langchain"""

from typing import Optional
from dataherald.sql_generator import SQLGenerator
from langchain.chains import SQLDatabaseSequentialChain as LangchainSQLChain
from langchain import LLMChain, OpenAI
from overrides import override


class LangChainSQLGenerator(SQLGenerator):
    @override
    def generate_response(self, user_question: str) -> str:
        print('Generating SQL response to question: ', user_question)
        return "That worked!"
    



    

   