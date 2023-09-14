from bson.objectid import ObjectId

from dataherald.types import NLQueryResponse

DB_COLLECTION = "nl_query_responses"


class NLQueryResponseRepository:
    def __init__(self, storage):
        self.storage = storage

    def insert(self, nl_query_response: NLQueryResponse) -> NLQueryResponse:
        nl_query_response.id = self.storage.insert_one(
            DB_COLLECTION, nl_query_response.dict(exclude={"id"})
        )
        return nl_query_response

    def find_one(self, query: dict) -> NLQueryResponse | None:
        row = self.storage.find_one(DB_COLLECTION, query)
        if not row:
            return None
        row["id"] = row["_id"]
        return NLQueryResponse(**row)

    def update(self, nl_query_response: NLQueryResponse) -> NLQueryResponse:
        self.storage.update_or_create(
            DB_COLLECTION,
            {"_id": ObjectId(nl_query_response.id)},
            nl_query_response.dict(exclude={"id"}),
        )
        return nl_query_response

    def find_by_id(self, id: str) -> NLQueryResponse | None:
        row = self.storage.find_one(DB_COLLECTION, {"_id": ObjectId(id)})
        if not row:
            return None
        row["id"] = row["_id"]
        return NLQueryResponse(**row)
