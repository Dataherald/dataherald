from bson.objectid import ObjectId

from dataherald.types import Prompt

DB_COLLECTION = "prompts"


class PromptNotFoundError(Exception):
    pass


class PromptRepository:
    def __init__(self, storage):
        self.storage = storage

    def insert(self, prompt: Prompt) -> Prompt:
        prompt_dict = prompt.dict(exclude={"id"})
        prompt.id = str(self.storage.insert_one(DB_COLLECTION, prompt_dict))
        return prompt

    def find_one(self, query: dict) -> Prompt | None:
        row = self.storage.find_one(DB_COLLECTION, query)
        if not row:
            return None
        row["id"] = str(row["_id"])
        return Prompt(**row)

    def find_by_id(self, id: str) -> Prompt | None:
        row = self.storage.find_one(DB_COLLECTION, {"_id": ObjectId(id)})
        if not row:
            return None
        row["id"] = str(row["_id"])
        return Prompt(**row)

    def find_by(self, query: dict, page: int = 1, limit: int = 10) -> list[Prompt]:
        rows = self.storage.find(DB_COLLECTION, query, page=page, limit=limit)
        result = []
        for row in rows:
            row["id"] = str(row["_id"])
            result.append(Prompt(**row))
        return result