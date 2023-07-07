from abc import ABC, abstractmethod
from typing import Any, List

from dataherald.config import Component
from dataherald.eval import Evaluation
from dataherald.types import DataDefinitionType, NLQueryResponse


class API(Component, ABC):
    @abstractmethod
    def heartbeat(self) -> int:
        """Returns the current server time in nanoseconds to check if the server is alive"""
        pass

    @abstractmethod
    def answer_question(self, question: str) -> NLQueryResponse:
        pass

    @abstractmethod
    def evaluate_question(self, question: str, golden_sql: str) -> Evaluation:
        pass

    @abstractmethod
    def connect_database(self, question: str) -> str:
        pass

    @abstractmethod
    def add_golden_records(self, golden_records: List) -> bool:
        pass
