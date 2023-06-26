"""Base class that all evaluators should inherit from."""
from abc import ABC, abstractmethod
from dataherald.config import Component, System
from typing import Any, Optional, Dict


class EvaluatorBase(Component, ABC):
    def __init__(self, sytstem: System):
        pass

    @abstractmethod
    def evaluate(self, question:str , sql:str , tables_used) -> bool:
        """Evaluates a question and SQL pair."""

  