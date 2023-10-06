from langchain.chains import LLMChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

from dataherald.model.chat_model import ChatModel
from dataherald.repositories.database_connections import DatabaseConnectionRepository
from dataherald.repositories.question import QuestionRepository
from dataherald.sql_database.base import SQLDatabase
from dataherald.sql_generator.create_sql_query_status import create_sql_query_status
from dataherald.types import Response

SYSTEM_TEMPLATE = """ Given a Question, a Sql query and the sql query result try to answer the question
If the sql query result doesn't answer the question just say 'I don't know'
"""

HUMAN_TEMPLATE = """ Answer the question given the sql query and the sql query result.
Question: {question}
SQL query: {sql_query}
SQL query result: {sql_query_result}
"""


class GeneratesNlAnswer:
    def __init__(self, system, storage):
        self.system = system
        self.storage = storage
        self.model = ChatModel(self.system)

    def execute(self, query_response: Response) -> Response:
        question_repository = QuestionRepository(self.storage)
        question = question_repository.find_by_id(query_response.question_id)

        db_connection_repository = DatabaseConnectionRepository(self.storage)
        database_connection = db_connection_repository.find_by_id(
            question.db_connection_id
        )
        self.llm = self.model.get_model(
            database_connection=database_connection,
            temperature=0,
        )
        database = SQLDatabase.get_sql_engine(database_connection)
        query_response = create_sql_query_status(
            database, query_response.sql_query, query_response
        )
        system_message_prompt = SystemMessagePromptTemplate.from_template(
            SYSTEM_TEMPLATE
        )
        human_message_prompt = HumanMessagePromptTemplate.from_template(HUMAN_TEMPLATE)
        chat_prompt = ChatPromptTemplate.from_messages(
            [system_message_prompt, human_message_prompt]
        )
        chain = LLMChain(llm=self.llm, prompt=chat_prompt)
        nl_resp = chain.run(
            question=question.question,
            sql_query=query_response.sql_query,
            sql_query_result=str(query_response.sql_query_result),
        )
        query_response.response = nl_resp
        return query_response
