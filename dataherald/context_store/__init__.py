from abc import ABC, abstractmethod
from typing import Any, List

from dataherald.config import Component, System
from dataherald.db import DB
from dataherald.vector_store import VectorStore


class ContextStore(Component, ABC):
    DocStore: DB
    VectorStore: VectorStore
    golden_record_collection = "golden-records"
    doc_store_collection = "table_meta_data"

    @abstractmethod
    def __init__(self, system: System):
        self.system = system
        self.db = self.system.instance(DB)
        self.vector_store = self.system.instance(VectorStore)

    @abstractmethod
    def retrieve_context_for_question(self, nl_question: str) -> str | None:
        pass

    @abstractmethod
    def add_golden_records(self, golden_records: List) -> bool:
        pass

    @abstractmethod
    def add_table_metadata(self, table_name: str, table_metadata: dict) -> bool:
        pass
