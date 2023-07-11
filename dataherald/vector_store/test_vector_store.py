from typing import List

from overrides import override

from dataherald.config import System
from dataherald.vector_store import VectorStore


class TestVectorStore(VectorStore):
    def __init__(self, system: System):
        super().__init__(system)

    @override
    def query(
        self, query_texts: List[str], collection: str, num_results: int  # noqa: ARG002
    ) -> list:
        return {"ids": []}

    @override
    def add_record(
        self, documents: str, collection: str, metadata: List, ids: List  # noqa: ARG002
    ):
        pass

    @override
    def delete_collection(self, collection: str):  # noqa: ARG002
        pass

    @override
    def create_collection(self, collection: str):  # noqa: ARG002
        pass
