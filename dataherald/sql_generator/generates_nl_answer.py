from langchain.chains import LLMChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

from dataherald.model.chat_model import ChatModel
from dataherald.repositories.database_connections import DatabaseConnectionRepository
from dataherald.repositories.nl_question import NLQuestionRepository
from dataherald.sql_database.base import SQLDatabase
from dataherald.sql_generator.create_sql_query_status import create_sql_query_status
from dataherald.types import NLQueryResponse

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
        model = ChatModel(self.system)
        self.llm = model.get_model(temperature=0)

    def execute(self, nl_query_response: NLQueryResponse) -> NLQueryResponse:
        nl_question_repository = NLQuestionRepository(self.storage)
        nl_question = nl_question_repository.find_by_id(
            nl_query_response.nl_question_id
        )

        db_connection_repository = DatabaseConnectionRepository(self.storage)
        database_connection = db_connection_repository.find_by_id(
            nl_question.db_connection_id
        )
        database = SQLDatabase.get_sql_engine(database_connection)
        nl_query_response = create_sql_query_status(
            database, nl_query_response.sql_query, nl_query_response
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
            question=nl_question.question,
            sql_query=nl_query_response.sql_query,
            sql_query_result=str(nl_query_response.sql_query_result),
        )
        nl_query_response.nl_response = nl_resp
        return nl_query_response
