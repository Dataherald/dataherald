from abc import ABC, abstractmethod

from pydantic import BaseModel, Field, confloat

from dataherald.config import Component, System
from dataherald.model.chat_model import ChatModel
from dataherald.sql_database.base import SQLDatabase
from dataherald.sql_database.models.types import DatabaseConnection
from dataherald.types import LLMConfig, Prompt, SQLGeneration


class Evaluation(BaseModel):
    id: str | None = Field(alias="_id")
    question_id: str | None = Field(alias="q_id")
    answer_id: str | None = Field(alias="a_id")
    score: confloat(ge=0, le=1) = 0.5


class Evaluator(Component, ABC):
    database: SQLDatabase
    acceptance_threshold: confloat(ge=0, le=1) = 0.8
    llm_config: LLMConfig
    llm: ChatModel | None = None

    def __init__(self, system: System):
        self.system = system
        self.model = ChatModel(self.system)

    def get_confidence_score(
        self,
        user_prompt: Prompt,
        sql_generation: SQLGeneration,
        database_connection: DatabaseConnection,
    ) -> confloat:
        """Determines if a generated response from the engine is acceptable considering the ACCEPTANCE_THRESHOLD"""
        evaluation = self.evaluate(
            user_prompt=user_prompt,
            sql_generation=sql_generation,
            database_connection=database_connection,
        )
        return evaluation.score

    @abstractmethod
    def evaluate(
        self,
        user_prompt: Prompt,
        sql_generation: SQLGeneration,
        database_connection: DatabaseConnection,
    ) -> Evaluation:
        """Evaluates a question with an SQL pair."""
