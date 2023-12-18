from overrides import override
from pydantic import confloat

from dataherald.config import System
from dataherald.eval import Evaluation, Evaluator
from dataherald.sql_database.models.types import DatabaseConnection
from dataherald.types import Prompt, SQLGeneration


class TestEvaluator(Evaluator):
    def __init__(self, system: System):
        pass

    @override
    def get_confidence_score(
        self,
        user_prompt: Prompt,
        sql_generation: SQLGeneration,
        database_connection: DatabaseConnection,
    ) -> confloat:
        score: confloat(ge=0, le=1) = 1.0
        return score

    @override
    def evaluate(
        self,
        user_prompt: Prompt,
        sql_generation: SQLGeneration,
        database_connection: DatabaseConnection,
    ) -> Evaluation:
        return Evaluation(question_id="0", answer_id="0", score=0.8)
