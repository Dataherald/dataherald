import os
from typing import Any, List

import pinecone
from langchain.embeddings import OpenAIEmbeddings
from overrides import override

from dataherald.config import System
from dataherald.db import DB
from dataherald.repositories.database_connections import DatabaseConnectionRepository
from dataherald.vector_store import VectorStore

EMBEDDING_MODEL = "text-embedding-ada-002"


class Pinecone(VectorStore):
    def __init__(self, system: System):
        super().__init__(system)
        api_key = os.environ.get("PINECONE_API_KEY")
        environment = os.environ.get("PINECONE_ENVIRONMENT")
        if api_key is None:
            raise ValueError("PINECONE_API_KEY environment variable not set")
        if environment is None:
            raise ValueError("PINECONE_ENVIRONMENT environment variable not set")
        pinecone.init(api_key=api_key, environment=environment)

    @override
    def query(
        self,
        query_texts: List[str],
        db_connection_id: str,
        collection: str,
        num_results: int,
    ) -> list:
        index = pinecone.Index(collection)
        db_connection_repository = DatabaseConnectionRepository(
            self.system.instance(DB)
        )
        database_connection = db_connection_repository.find_by_id(db_connection_id)
        embedding = OpenAIEmbeddings(
            openai_api_key=database_connection.decrypt_api_key(), model=EMBEDDING_MODEL
        )
        xq = embedding.embed_query(query_texts[0])
        query_response = index.query(
            queries=[xq],
            filter={
                "db_connection_id": {"$eq": db_connection_id},
            },
            top_k=num_results,
            include_metadata=True,
        )
        return query_response.to_dict()["results"][0]["matches"]

    @override
    def add_record(
        self,
        documents: str,
        db_connection_id: str,
        collection: str,
        metadata: Any,
        ids: List,
    ):
        if collection not in pinecone.list_indexes():
            self.create_collection(collection)
        db_connection_repository = DatabaseConnectionRepository(
            self.system.instance(DB)
        )
        database_connection = db_connection_repository.find_by_id(db_connection_id)
        embedding = OpenAIEmbeddings(
            openai_api_key=database_connection.decrypt_api_key(), model=EMBEDDING_MODEL
        )
        index = pinecone.Index(collection)
        embeds = embedding.embed_documents([documents])
        record = [(ids[0], embeds, metadata[0])]
        index.upsert(vectors=record)

    @override
    def delete_record(self, collection: str, id: str):
        if collection not in pinecone.list_indexes():
            self.create_collection(collection)
        index = pinecone.Index(collection)
        index.delete(ids=[id])

    @override
    def delete_collection(self, collection: str):
        return pinecone.delete_index(collection)

    @override
    def create_collection(self, collection: str):
        pinecone.create_index(name=collection, dimension=1536, metric="cosine")
