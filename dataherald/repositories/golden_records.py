from bson.objectid import ObjectId

from dataherald.types import GoldenRecord

DB_COLLECTION = "golden_records"


class GoldenRecordRepository:
    def __init__(self, storage):
        self.storage = storage

    def insert(self, golden_record: GoldenRecord) -> GoldenRecord:
        golden_record.id = self.storage.insert_one(
            DB_COLLECTION, golden_record.dict(exclude={"id"})
        )
        return golden_record

    def find_one(self, query: dict) -> GoldenRecord | None:
        row = self.storage.find_one(DB_COLLECTION, query)
        if not row:
            return None
        return GoldenRecord(**row)

    def update(self, golden_record: GoldenRecord) -> GoldenRecord:
        self.storage.update_or_create(
            DB_COLLECTION,
            {"_id": ObjectId(golden_record.id)},
            golden_record.dict(exclude={"id"}),
        )
        return golden_record

    def find_by_id(self, id: str) -> GoldenRecord | None:
        row = self.storage.find_one(DB_COLLECTION, {"_id": ObjectId(id)})
        if not row:
            return None
        return GoldenRecord(**row)

    def find_all(self, namespace: str) -> list[GoldenRecord]:
        rows = self.storage.find_all_from_namespace(DB_COLLECTION, namespace)
        return [GoldenRecord(id=str(row["_id"]), **row) for row in rows]

    def delete_by_id(self, id: str) -> int:
        return self.storage.delete_by_id(DB_COLLECTION, id)
