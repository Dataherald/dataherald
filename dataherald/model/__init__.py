from abc import ABC, abstractmethod
from typing import Any

from dataherald.config import Component, System
from dataherald.sql_database.models.types import DatabaseConnection


class LLMModel(Component, ABC):
    model: Any

    @abstractmethod
    def __init__(self, system: System):
        self.system = system

    @abstractmethod
    def get_model(
        self,
        database_connection: DatabaseConnection,
        model_family: str ="openai",
        model_name: str = "gpt-4-32k",
        **kwargs: Any
    ) -> Any:
        pass
