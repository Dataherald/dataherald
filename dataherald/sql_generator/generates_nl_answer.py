import openai

from dataherald.repositories.nl_question import NLQuestionRepository
from dataherald.sql_database.base import SQLDatabase
from dataherald.sql_database.models.types import DatabaseConnection
from dataherald.sql_generator.create_sql_query_status import create_sql_query_status
from dataherald.types import NLQueryResponse


class GeneratesNlAnswer:
    def __init__(self, storage):
        self.storage = storage

    def execute(self, nl_query_response: NLQueryResponse) -> NLQueryResponse:
        nl_question_repository = NLQuestionRepository(self.storage)
        nl_question = nl_question_repository.find_by_id(
            nl_query_response.nl_question_id
        )

        db_connection = self.storage.find_one(
            "database_connection", {"alias": nl_question.db_alias}
        )
        database_connection = DatabaseConnection(**db_connection)
        database = SQLDatabase.get_sql_engine(database_connection)
        nl_query_response = create_sql_query_status(
            database, nl_query_response.sql_query, nl_query_response
        )
        chat_completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": """Given a Question, a Sql query and the sql query result try to answer the question,
                    if you don't know the answer just say 'I don't know'""",
                },
                {
                    "role": "user",
                    "content": f"""Question: {nl_question.question},
                    Sql query: {nl_query_response.sql_query}, and
                    Sql query result:{str(nl_query_response.sql_query_result)}""",
                },
            ],
        )
        nl_query_response.nl_response = chat_completion["choices"][0]["message"][
            "content"
        ]
        return nl_query_response
