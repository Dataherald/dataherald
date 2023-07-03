from overrides import override

from dataherald.config import System
from dataherald.sql_generator import SQLGenerator
from dataherald.types import NLQuery, NLQueryResponse


class TestGenerator(SQLGenerator):
    def __init__(self, system: System):
        pass

    @override
    def generate_response(
        self, user_question: NLQuery  # noqa: ARG002
    ) -> NLQueryResponse:
        return NLQueryResponse(
            nl_question_id=None,
            nl_response="Foo response",
            intermediate_steps=["foo"],
            sql_query="bar",
        )
