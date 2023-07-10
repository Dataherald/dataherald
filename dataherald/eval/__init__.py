from abc import ABC, abstractmethod

from pydantic import BaseModel, Field, confloat

from dataherald.config import Component, System

ACCEPTANCE_THRESHOLD: confloat(ge=0, le=1) = 0.8


class Evaluation(BaseModel):
    id: str | None = Field(alias="_id")
    question_id: str
    score: confloat(ge=0, le=1) = 0.8


class Evaluator(Component, ABC):
    def __init__(self, system: System):
        pass

    def is_acceptable_response(self, question: str) -> bool:
        """Determines if a generated response from the engine is acceptable considering the ACCEPTANCE_THRESHOLD"""
        golden_sql = self.get_golden_sql(question)
        evaluation = self.evaluate(question=question, golden_sql=golden_sql)
        return evaluation.score >= ACCEPTANCE_THRESHOLD

    @abstractmethod
    def get_golden_sql(self, question: str) -> str:
        """Obtains the golden SQL for the given question"""

    @abstractmethod
    def evaluate(self, question: str, golden_sql: str) -> Evaluation:
        """Evaluates a question with an SQL pair."""
