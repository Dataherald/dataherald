from overrides import override
from typing import Any
import chromadb
from chromadb.config import Settings

from dataherald.config import System
from dataherald.context_store import ContextStore


class DefaultContextStore(ContextStore):
    golden_query_collection: Any

    def __init__(self, system: System):
        super().__init__(system)
        chromaClient = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet",
                                                     persist_directory="/app/chroma"))
        self.golden_query_collection = chromaClient.get_collection("golden_queries")
    @override
    def retrieve_context_for_question(self, nl_question: str) -> str:
        print(nl_question)
        return self.golden_query_collection.query(
            query_texts = [nl_question],
            n_results = 1
        )

    @override
    def add_golden_sql(self, nl_question: str, golden_sql: str) -> bool:
        self.golden_query_collection.add(
            documents =[nl_question],
            metadatas = [{"table_used": golden_sql}],
            ids=['1']
        )

    @override
    def add_table_metadata(self, table_name: str, table_metadata: dict) -> bool:
        return super().add_table_metadata(table_name, table_metadata)
