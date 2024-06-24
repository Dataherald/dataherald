import os
from typing import Any, List

from astrapy.api import APIRequestError
from astrapy.db import AstraDB
from langchain_openai import OpenAIEmbeddings
from overrides import override
from sql_metadata import Parser

from dataherald.config import System
from dataherald.db import DB
from dataherald.repositories.database_connections import DatabaseConnectionRepository
from dataherald.types import GoldenSQL
from dataherald.vector_store import VectorStore

EMBEDDING_MODEL = "text-embedding-3-small"


class Astra(VectorStore):
    def __init__(self, system: System):
        super().__init__(system)
        astra_db_api_endpoint = os.environ.get("ASTRA_DB_API_ENDPOINT")
        astra_db_application_token = os.environ.get("ASTRA_DB_APPLICATION_TOKEN")
        if astra_db_api_endpoint is None:
            raise ValueError("ASTRA_DB_API_ENDPOINT environment variable not set")
        if astra_db_application_token is None:
            raise ValueError("ASTRA_DB_APPLICATION_TOKEN environment variable not set")
        self.db = AstraDB(
            token=os.environ["ASTRA_DB_APPLICATION_TOKEN"],
            api_endpoint=os.environ["ASTRA_DB_API_ENDPOINT"],
            namespace="default_keyspace",
        )

    def collection_name_formatter(self, collection: str) -> str:
        return collection.replace("-", "_")

    @override
    def query(
        self,
        query_texts: List[str],
        db_connection_id: str,
        collection: str,
        num_results: int,
    ) -> list:
        collection = self.collection_name_formatter(collection)
        try:
            existing_collections = self.db.get_collections()["status"]["collections"]
        except APIRequestError:
            existing_collections = []
        if collection not in existing_collections:
            raise ValueError(f"Collection {collection} does not exist")
        astra_collection = self.db.collection(collection)
        db_connection_repository = DatabaseConnectionRepository(
            self.system.instance(DB)
        )
        database_connection = db_connection_repository.find_by_id(db_connection_id)
        embedding = OpenAIEmbeddings(
            openai_api_key=database_connection.decrypt_api_key(), model=EMBEDDING_MODEL
        )
        xq = embedding.embed_query(query_texts[0])
        returened_results = astra_collection.vector_find(
            vector=xq,
            limit=num_results,
            filter={"db_connection_id": {"$eq": db_connection_id}},
            include_similarity=True,
        )
        return self.convert_to_pinecone_object_model(returened_results)

    @override
    def add_records(self, golden_sqls: List[GoldenSQL], collection: str):
        collection = self.collection_name_formatter(collection)
        try:
            existing_collections = self.db.get_collections()["status"]["collections"]
        except APIRequestError:
            existing_collections = []
        if collection not in existing_collections:
            self.create_collection(collection)
        astra_collection = self.db.collection(collection)
        db_connection_repository = DatabaseConnectionRepository(
            self.system.instance(DB)
        )
        database_connection = db_connection_repository.find_by_id(
            str(golden_sqls[0].db_connection_id)
        )
        embedding = OpenAIEmbeddings(
            openai_api_key=database_connection.decrypt_api_key(), model=EMBEDDING_MODEL
        )
        embeds = embedding.embed_documents(
            [record.prompt_text for record in golden_sqls]
        )
        records = []
        for key in range(len(golden_sqls)):
            records.append(
                {
                    "_id": str(golden_sqls[key].id),
                    "$vector": embeds[key],
                    "tables_used": (
                        ", ".join(Parser(golden_sqls[key].sql))
                        if isinstance(Parser(golden_sqls[key].sql), list)
                        else ""
                    ),
                    "db_connection_id": str(golden_sqls[key].db_connection_id),
                }
            )
        astra_collection.chunked_insert_many(
            documents=records, chunk_size=10, concurrency=1
        )

    @override
    def add_record(
        self,
        documents: str,
        db_connection_id: str,
        collection: str,
        metadata: Any,
        ids: List,
    ):
        collection = self.collection_name_formatter(collection)
        try:
            existing_collections = self.db.get_collections()["status"]["collections"]
        except APIRequestError:
            existing_collections = []
        if collection not in existing_collections:
            self.create_collection(collection)
        astra_collection = self.db.collection(collection)
        db_connection_repository = DatabaseConnectionRepository(
            self.system.instance(DB)
        )
        database_connection = db_connection_repository.find_by_id(db_connection_id)
        embedding = OpenAIEmbeddings(
            openai_api_key=database_connection.decrypt_api_key(), model=EMBEDDING_MODEL
        )
        embeds = embedding.embed_documents([documents])
        astra_collection.insert_one({"_id": ids[0], "$vector": embeds, **metadata[0]})

    @override
    def delete_record(self, collection: str, id: str):
        collection = self.collection_name_formatter(collection)
        try:
            existing_collections = self.db.get_collections()["status"]["collections"]
        except APIRequestError:
            existing_collections = []
        if collection not in existing_collections:
            raise ValueError(f"Collection {collection} does not exist")
        astra_collection = self.db.collection(collection)
        astra_collection.delete_one(id)

    @override
    def delete_collection(self, collection: str):
        collection = self.collection_name_formatter(collection)
        return self.db.delete_collection(collection_name=collection)

    @override
    def create_collection(self, collection: str):
        collection = self.collection_name_formatter(collection)
        return self.db.create_collection(collection, dimension=1536, metric="cosine")

    def convert_to_pinecone_object_model(self, astra_results: dict) -> List:
        results = []
        for i in range(len(astra_results)):
            results.append(
                {
                    "id": astra_results[i]["_id"],
                    "score": astra_results[i]["$similarity"],
                }
            )
        return results
