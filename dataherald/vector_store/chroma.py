from typing import List, Any

import chromadb
from chromadb.config import Settings
from overrides import override

from dataherald.config import System
from dataherald.vector_store import VectorStore


class Chroma(VectorStore):
    def __init__(
        self,
        system: System,
        chroma_db_impl: str = "duckdb+parquet",
        persist_directory: str = "/app/chroma",
    ):
        super().__init__(system)
        self.chroma_client = chromadb.Client(
            Settings(chroma_db_impl=chroma_db_impl, persist_directory=persist_directory)
        )

    @override
    def query(self, query_texts: List[str], collection: str, num_results: int) -> list:
        try:
            target_collection = self.chroma_client.get_collection(collection)
        except ValueError:
            return []
        return target_collection.query(query_texts=query_texts, n_results=num_results)

    @override
    def add_record(self, documents: str, collection: str, metadata: Any, ids: List):
        target_collection = self.chroma_client.get_or_create_collection(collection)
        target_collection.add(documents=documents, metadatas=metadata, ids=ids)

    @override
    def delete_collection(self, collection: str):
        return super().delete_collection(collection)

    @override
    def create_collection(self, collection: str):
        return super().create_collection(collection)
