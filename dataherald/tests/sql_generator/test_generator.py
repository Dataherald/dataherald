from typing import List

from overrides import override

from dataherald.config import System
from dataherald.sql_database.models.types import DatabaseConnection
from dataherald.sql_generator import SQLGenerator
from dataherald.types import Question, Response


class TestGenerator(SQLGenerator):
    def __init__(self, system: System):
        pass

    @override
    def generate_response(
        self,
        user_question: Question,
        database_connection: DatabaseConnection,
        context: List[dict] = None,  # noqa: ARG002
        generate_csv: bool = None,
    ) -> Response:
        return Response(
            question_id="651f2d76275132d5b65175eb",
            response="Foo response",
            intermediate_steps=["foo"],
            sql_query="bar",
            generate_csv=None,
        )
