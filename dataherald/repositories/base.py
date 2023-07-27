from dataherald.types import NLQueryResponse

DB_COLLECTION = "nl_query_response"


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
        return NLQueryResponse(**row)
