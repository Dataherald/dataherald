from bson.objectid import ObjectId

from dataherald.types import Vulnerability

DB_COLLECTION = "vulnerabilities"


class VulnerabilityRepository:
    def __init__(self, storage):
        self.storage = storage

    def find_one(self, query: dict) -> Vulnerability | None:
        row = self.storage.find_one(DB_COLLECTION, query)
        if not row:
            return None
        row["id"] = str(row["_id"])
        return Vulnerability(**row)

    def find_by_id(self, id: str) -> Vulnerability | None:
        row = self.storage.find_one(DB_COLLECTION, {"_id": ObjectId(id)})
        if not row:
            return None
        row["id"] = str(row["_id"])
        return Vulnerability(**row)

    def find_by(
        self, query: dict, page: int = 1, limit: int = 10
    ) -> list[Vulnerability]:
        rows = self.storage.find(DB_COLLECTION, query, page=page, limit=limit)
        result = []
        for row in rows:
            row["id"] = str(row["_id"])
            result.append(Vulnerability(**row))
        return result

    def find_all(self, page: int = 0, limit: int = 0) -> list[Vulnerability]:
        rows = self.storage.find_all(DB_COLLECTION, page=page, limit=limit)
        result = []
        for row in rows:
            row["id"] = str(row["_id"])
            result.append(Vulnerability(**row))
        return result
