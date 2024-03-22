from typing import List

from overrides import override

from dataherald.config import System
from dataherald.sql_database.models.types import DatabaseConnection
from dataherald.sql_generator import SQLGenerator
from dataherald.types import Prompt, SQLGeneration


class TestGenerator(SQLGenerator):
    def __init__(self, system: System):
        pass

    @override
    def generate_response(
        self,
        user_prompt: Prompt,
        database_connection: DatabaseConnection,
        context: List[dict] = None,  # noqa: ARG002
        metadata: dict = None,  # noqa: ARG002
    ) -> SQLGeneration:
        return SQLGeneration(
            question_id="651f2d76275132d5b65175eb",
            sql="Foo response",
            status="bar",
        )
