import os
from typing import Any, List

import openai
import pinecone
from overrides import override

from dataherald.config import System
from dataherald.vector_store import VectorStore

EMBEDDING_MODEL = "text-embedding-ada-002"


class Pinecone(VectorStore):
    def __init__(self, system: System):
        super().__init__(system)
        api_key = os.environ.get("PINECONE_API_KEY")
        if api_key is None:
            raise ValueError("PINECONE_API_KEY environment variable not set")

        pinecone.init(api_key=api_key, environment="us-west4-gcp")

    @override
    def query(self, query_texts: List[str], collection: str, num_results: int) -> list:
        index = pinecone.Index(collection)
        xq = openai.Embedding.create(input=query_texts[0], engine=EMBEDDING_MODEL)[
            "data"
        ][0]["embedding"]
        query_response = index.query(
            queries=[xq], top_k=num_results, include_metadata=True
        )

        return query_response.to_dict()["results"][0]["matches"]

    @override
    def add_record(self, documents: str, collection: str, metadata: Any, ids: List):
        if collection not in pinecone.list_indexes():
            self.create_collection(collection)

        index = pinecone.Index(collection)
        res = openai.Embedding.create(input=[documents], engine=EMBEDDING_MODEL)
        embeds = [record["embedding"] for record in res["data"]]
        record = [(ids[0], embeds)]
        index.upsert(vectors=record, metadata=metadata[0])

    @override
    def delete_collection(self, collection: str):
        return pinecone.delete_index(collection)

    @override
    def create_collection(self, collection: str):
        pinecone.create_index(name=collection, dimension=1536, metric="cosine")
