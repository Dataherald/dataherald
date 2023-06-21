"""A wrapper for the SQL generation functions in langchain"""

from typing import Optional
from dataherald.sql_generation.base import SQLGenerator
from langchain.chains import SQLDatabaseSequentialChain as LangchainSQLChain
from langchain import LLMChain, OpenAI
from langchain.base_language import BaseLanguageModel

class LangChainSQLGenerator(SQLGenerator, LangchainSQLChain):
    llm: Optional[BaseLanguageModel] = None

   