import os
from abc import ABC, abstractmethod
from typing import List, Tuple

from dataherald.config import Component, System
from dataherald.db import DB
from dataherald.types import ContextFile, GoldenSQL, GoldenSQLRequest, Prompt
from dataherald.vector_store import VectorStore


class ContextStore(Component, ABC):
    DocStore: DB
    VectorStore: VectorStore
    doc_store_collection = "table_meta_data"

    @abstractmethod
    def __init__(self, system: System):
        self.system = system
        self.db = self.system.instance(DB)
        self.golden_sql_collection = os.environ.get(
            "GOLDEN_SQL_COLLECTION", "dataherald-staging"
        )
        self.context_files_collection = os.environ.get(
            "CONTEXT_FILES_COLLECTION", "context_files-staging"
        )
        self.vector_store = self.system.instance(VectorStore)

    @abstractmethod
    def retrieve_context_for_question(
        self, prompt: Prompt, number_of_samples: int = 3
    ) -> Tuple[List[dict] | None, List[dict] | None]:
        pass

    @abstractmethod
    def add_golden_sqls(self, golden_sqls: List[GoldenSQLRequest]) -> List[GoldenSQL]:
        pass

    @abstractmethod
    def remove_golden_sqls(self, ids: List) -> bool:
        pass

    @abstractmethod
    def add_context_file(self, context_file: ContextFile, content: str) -> ContextFile:
        pass

    @abstractmethod
    def delete_context_file(self, context_file: ContextFile) -> bool:
        pass
