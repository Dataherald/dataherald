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
        model_family="openai",
        model_name="gpt-4",
        **kwargs: Any
    ) -> Any:
        pass
