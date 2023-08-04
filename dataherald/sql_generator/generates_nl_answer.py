from datetime import date, datetime

import openai

from dataherald.repositories.nl_question import NLQuestionRepository
from dataherald.sql_database.base import SQLDatabase
from dataherald.sql_database.models.types import DatabaseConnection
from dataherald.types import NLQueryResponse, SQLQueryResult


class GeneratesNlAnswer:
    def __init__(self, storage):
        self.storage = storage

    def create_sql_query_status(
        self, db: SQLDatabase, query: str, response: NLQueryResponse
    ) -> NLQueryResponse:
        """Find the sql query status and populate the fields sql_query_result, sql_generation_status, and error_message"""
        response.sql_query = query
        if query == "":
            response.sql_generation_status = "NONE"
            response.sql_query_result = None
            response.error_message = None
        else:
            try:
                execution = db.engine.execute(query)
                columns = execution.keys()
                result = execution.fetchall()
                if len(result) == 0:
                    response.sql_query_result = None
                else:
                    columns = [item for item in columns]  # noqa: C416
                    rows = []
                    for row in result:
                        modified_row = {}
                        for key, value in zip(row.keys(), row, strict=True):
                            if (
                                type(value) is date
                            ):  # Check if the value is an instance of datetime.date
                                modified_row[key] = datetime(
                                    value.year, value.month, value.day
                                )
                            else:
                                modified_row[key] = value
                        rows.append(modified_row)
                    response.sql_query_result = SQLQueryResult(
                        columns=columns, rows=rows
                    )
                response.sql_generation_status = "VALID"
                response.error_message = None
            except Exception as e:
                response.sql_generation_status = "INVALID"
                response.sql_query_result = None
                response.error_message = str(e)
        return response

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
        nl_query_response = self.create_sql_query_status(
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
