from bson.objectid import ObjectId

from dataherald.types import ContextFile

DB_COLLECTION = "context_files"


class ContextFileNotFoundError(Exception):
    pass


class ContextFileRepository:
    def __init__(self, storage):
        self.storage = storage

    def insert(self, context_file: ContextFile) -> ContextFile:
        context_file.id = str(
            self.storage.insert_one(DB_COLLECTION, context_file.dict(exclude={"id"}))
        )
        return context_file

    def find_one(self, query: dict) -> ContextFile | None:
        row = self.storage.find_one(DB_COLLECTION, query)
        if not row:
            return None
        obj = ContextFile(**row)
        obj.id = str(row["_id"])
        return obj

    def update(self, context_file: ContextFile) -> ContextFile:
        self.storage.update_or_create(
            DB_COLLECTION,
            {"_id": ObjectId(context_file.id)},
            context_file.dict(exclude={"id"}),
        )
        return context_file

    def find_by_id(self, id: str) -> ContextFile | None:
        row = self.storage.find_one(DB_COLLECTION, {"_id": ObjectId(id)})
        if not row:
            return None
        obj = ContextFile(**row)
        obj.id = str(row["_id"])
        return obj

    def find_all(self) -> list[ContextFile]:
        rows = self.storage.find_all(DB_COLLECTION)
        result = []
        for row in rows:
            obj = ContextFile(**row)
            obj.id = str(row["_id"])
            result.append(obj)
        return result

    def delete_by_id(self, id: str) -> int:
        return self.storage.delete_by_id(DB_COLLECTION, id)
