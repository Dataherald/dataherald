from bson.objectid import ObjectId

from dataherald.types import Finetuning

DB_COLLECTION = "finetunings"


class FinetuningsRepository:
    def __init__(self, storage):
        self.storage = storage

    def insert(self, model: Finetuning) -> Finetuning:
        model.id = str(
            self.storage.insert_one(DB_COLLECTION, model.dict(exclude={"id"}))
        )
        return model

    def find_one(self, query: dict) -> Finetuning | None:
        row = self.storage.find_one(DB_COLLECTION, query)
        if not row:
            return None
        obj = Finetuning(**row)
        obj.id = str(row["_id"])
        return obj

    def update(self, model: Finetuning) -> Finetuning:
        self.storage.update_or_create(
            DB_COLLECTION,
            {"_id": ObjectId(model.id)},
            model.dict(exclude={"id"}),
        )
        return model

    def find_by_id(self, id: str) -> Finetuning | None:
        row = self.storage.find_one(DB_COLLECTION, {"_id": ObjectId(id)})
        if not row:
            return None
        obj = Finetuning(**row)
        obj.id = str(row["_id"])
        return obj

    def find_by(self, query: dict, page: int = 0, limit: int = 0) -> list[Finetuning]:
        if page > 0 and limit > 0:
            rows = self.storage.find(DB_COLLECTION, query, page=page, limit=limit)
        else:
            rows = self.storage.find(DB_COLLECTION, query)
        result = []
        for row in rows:
            obj = Finetuning(**row)
            obj.id = str(row["_id"])
            result.append(obj)
        return result

    def find_all(self, page: int = 0, limit: int = 0) -> list[Finetuning]:
        rows = self.storage.find_all(DB_COLLECTION, page=page, limit=limit)
        result = []
        for row in rows:
            obj = Finetuning(**row)
            obj.id = str(row["_id"])
            result.append(obj)
        return result

    def delete_by_id(self, id: str) -> int:
        return self.storage.delete_by_id(DB_COLLECTION, id)
