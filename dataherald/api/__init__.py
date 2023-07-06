from abc import ABC, abstractmethod

from dataherald.config import Component
from dataherald.eval import Evaluation
from dataherald.types import ContextType, NLQueryResponse
from typing import Any


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
    def add_context(self, type: ContextType, context_document_handler: Any) -> bool:
        pass
