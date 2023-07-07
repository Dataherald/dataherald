from abc import ABC, abstractmethod
from typing import Any, List

from dataherald.config import Component, System


class ContextStore(Component, ABC):


    @abstractmethod
    def __init__(self, system: System):
        self.system = system


    @abstractmethod
    def retrieve_context_for_question(self, nl_question: str) -> str | None:
        pass

    @abstractmethod
    def add_golden_records(self, golden_records:List) -> bool:
        pass

    @abstractmethod
    def add_table_metadata(self, table_name: str, table_metadata: dict) -> bool:
        pass
