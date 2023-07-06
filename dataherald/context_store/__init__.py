from abc import ABC, abstractmethod
from typing import Any

from dataherald.config import Component, System


class ContextStore(Component, ABC):
    vectorDB: Any

    @abstractmethod
    def __init__(self, system: System):
        self.system = system


    @abstractmethod
    def retrieve_context_for_question(self, nl_question: str) -> str:
        pass

    """@abstractmethod
    def add_golden_sql(self, nl_question: str, golden_sql: str) -> bool:
        pass

    @abstractmethod
    def add_table_metadata(self, table_name: str, table_metadata: dict) -> bool:
        pass"""
