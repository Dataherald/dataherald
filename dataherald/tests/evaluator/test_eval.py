from overrides import override

from dataherald.config import System
from dataherald.eval import Evaluation, Evaluator
from dataherald.sql_database.models.types import DatabaseConnection
from dataherald.types import NLQuery, NLQueryResponse


class TestEvaluator(Evaluator):
    def __init__(self, system: System):
        pass

    @override
    def is_acceptable_response(
        self,
        question: NLQuery,
        generated_answer: NLQueryResponse,
        database_connection: DatabaseConnection,
    ) -> bool:
        return True

    @override
    def evaluate(
        self,
        question: NLQuery,
        generated_answer: NLQueryResponse,
        database_connection: DatabaseConnection,
    ) -> Evaluation:
        return Evaluation(question_id="0", answer_id="0", score=0.8)
