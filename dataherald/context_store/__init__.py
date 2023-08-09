import os
from abc import ABC, abstractmethod
from typing import Any, List

from dataherald.config import Component, System
from dataherald.db import DB
from dataherald.types import NLQuery
from dataherald.vector_store import VectorStore


class ContextStore(Component, ABC):
    DocStore: DB
    VectorStore: VectorStore
    doc_store_collection = "table_meta_data"

    @abstractmethod
    def __init__(self, system: System):
        self.system = system
        self.db = self.system.instance(DB)
        self.golden_record_collection = os.environ.get("PINECONE_COLLECTION")
        if self.golden_record_collection is None:
            raise ValueError("PINECONE_COLLECTION environment variable not set")
        self.vector_store = self.system.instance(VectorStore)

    @abstractmethod
    def retrieve_context_for_question(
        self, nl_question: NLQuery, number_of_samples: int = 3
    ) -> List[dict] | None:
        pass

    @abstractmethod
    def add_golden_records(self, golden_records: List) -> bool:
        pass

    @abstractmethod
    def remove_golden_records(self, ids: List) -> bool:
        pass

    @abstractmethod
    def add_table_metadata(self, table_name: str, table_metadata: dict) -> bool:
        pass
