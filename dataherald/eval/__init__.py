from abc import ABC, abstractmethod

from dataherald.config import Component, System


class Evaluator(Component, ABC):
    def __init__(self, system: System):
        pass

    @abstractmethod
    def evaluate(self, question: str, sql: str, tables_used) -> bool:
        """Evaluates a question and SQL pair."""
