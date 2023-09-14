from bson.objectid import ObjectId

from dataherald.types import NLQuery

DB_COLLECTION = "nl_questions"


class NLQuestionRepository:
    def __init__(self, storage):
        self.storage = storage

    def insert(self, nl_query: NLQuery) -> NLQuery:
        nl_query.id = self.storage.insert_one(
            DB_COLLECTION, nl_query.dict(exclude={"id"})
        )
        return nl_query

    def find_one(self, query: dict) -> NLQuery | None:
        row = self.storage.find_one(DB_COLLECTION, query)
        if not row:
            return None
        return NLQuery(**row)

    def find_by_id(self, id: str) -> NLQuery | None:
        row = self.storage.find_one(DB_COLLECTION, {"_id": ObjectId(id)})
        if not row:
            return None
        return NLQuery(**row)
