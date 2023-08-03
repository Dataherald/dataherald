from overrides import override
from pydantic import confloat

from dataherald.config import System
from dataherald.eval import Evaluation, Evaluator
from dataherald.sql_database.models.types import DatabaseConnection
from dataherald.types import NLQuery, NLQueryResponse


class TestEvaluator(Evaluator):
    def __init__(self, system: System):
        pass

    @override
    def get_confidence_score(
        self,
        question: NLQuery,
        generated_answer: NLQueryResponse,
        database_connection: DatabaseConnection,
    ) -> confloat(ge=0, le=1):
        return 1.0

    @override
    def evaluate(
        self,
        question: NLQuery,
        generated_answer: NLQueryResponse,
        database_connection: DatabaseConnection,
    ) -> Evaluation:
        return Evaluation(question_id="0", answer_id="0", score=0.8)
