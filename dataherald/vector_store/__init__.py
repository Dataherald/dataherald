from abc import ABC, abstractmethod
from typing import Any, List

from dataherald.config import Component, System


class VectorStore(Component, ABC):
    collections: List[str]

    @abstractmethod
    def __init__(self, system: System):
        self.system = system

    @abstractmethod
    def query(self, query_texts: List[str], collection: str, num_results: int) -> list:
        pass

    @abstractmethod
    def create_collection(self, collection: str):
        pass

    @abstractmethod
    def add_record(self, documents: str, collection: str, metadata: List, ids: List):
        pass

    @abstractmethod
    def delete_collection(self, collection: str):
        pass
