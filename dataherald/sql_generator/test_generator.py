from overrides import override

from dataherald.sql_generator import SQLGenerator
from dataherald.types import NLQuery, NLQueryResponse


class TestGenerator(SQLGenerator):
    @override
    def generate_response(
        self, user_question: NLQuery  # noqa: ARG002
    ) -> NLQueryResponse:
        return NLQueryResponse(
            nl_question_id=None,
            nl_response=None,
            intermediate_steps=["foo"],
            sql_query="bar",
        )
