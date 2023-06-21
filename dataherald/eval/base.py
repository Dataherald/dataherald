"""Base class that all evaluators should inherit from."""
from abc import ABC, abstractmethod
from typing import Any, Optional, Dict


class EvaluatorBase(ABC):

    @abstractmethod
    def evaluate(self, question, sql, tables_used) -> bool:
        """Evaluates a question and SQL pair."""

  