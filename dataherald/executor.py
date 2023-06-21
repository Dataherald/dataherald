from dataherald.smart_cache.in_memory import InMemoryCache
from dataherald.eval.simple_evaluator import SimpleEvaluator
from dataherald.sql_database.base import SQLDatabase
from dataherald.sql_generation.langchain_sql import LangChainSQLGenerator
from langchain.chat_models import ChatOpenAI

OPENAI_API_KEY = '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'


def single_question(user_question:str, llm= None) -> str:
    """A function that takes a user question and returns a SQL query."""
    cache = InMemoryCache()
    evaluator = SimpleEvaluator()
    database = SQLDatabase.from_uri("sqlite://")
    sql_generator = LangChainSQLGenerator(database=database)
    if cache.lookup(user_question) != None:
        return cache(user_question)
    else:
        generated_sql = database.run_sql(user_question)
        if evaluator.evaluate(user_question, generated_sql) == True:
            cache.add(user_question, generated_sql)
            return generated_sql
        


if __name__ == "__main__":
    llm = ChatOpenAI(temperature=0, openai_api_key=OPENAI_API_KEY, model_name='gpt-3.5-turbo')
    single_question("What is the average age of people in the table?", llm=llm)