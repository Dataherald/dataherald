from abc import ABC, abstractmethod

from pydantic import BaseModel, confloat

from dataherald.config import Component, System
from dataherald.eval import ACCEPTANCE_THRESHOLD


class Evaluation(BaseModel):
    id: str
    question_id: str
    score: confloat(ge=0, le=1) = 0.8


class Evaluator(Component, ABC):
    def __init__(self, system: System):
        pass

    def is_acceptable_response(self, question: str) -> bool:
        """Determines if a generated response from the engine is acceptable considering the ACCEPTANCE_THRESHOLD"""
        golden_sql = self.get_golden_sql(question)
        evaluation = self._evaluate(question=question, golden_sql=golden_sql)
        return evaluation.score >= ACCEPTANCE_THRESHOLD

    @abstractmethod
    def get_golden_sql(self, question: str) -> bool:
        """Obtains the golden SQL for the given question"""

    @abstractmethod
    def _evaluate(self, question: str, golden_sql: str) -> Evaluation:
        """Evaluates a question with an SQL pair."""
