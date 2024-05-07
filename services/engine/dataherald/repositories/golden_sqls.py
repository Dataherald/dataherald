from bson.objectid import ObjectId

from dataherald.types import GoldenSQL

DB_COLLECTION = "golden_sqls"


class GoldenSQLNotFoundError(Exception):
    pass


class GoldenSQLRepository:
    def __init__(self, storage):
        self.storage = storage

    def insert(self, golden_sql: GoldenSQL) -> GoldenSQL:
        golden_sql_dict = golden_sql.dict(exclude={"id"})
        golden_sql_dict["db_connection_id"] = str(golden_sql.db_connection_id)
        golden_sql.id = str(self.storage.insert_one(DB_COLLECTION, golden_sql_dict))
        return golden_sql

    def find_one(self, query: dict) -> GoldenSQL | None:
        row = self.storage.find_one(DB_COLLECTION, query)
        if not row:
            return None
        row["id"] = str(row["_id"])
        row["db_connection_id"] = str(row["db_connection_id"])
        return GoldenSQL(**row)

    def update(self, golden_sql: GoldenSQL) -> GoldenSQL:
        golden_sql_dict = golden_sql.dict(exclude={"id"})
        golden_sql_dict["db_connection_id"] = str(golden_sql.db_connection_id)

        self.storage.update_or_create(
            DB_COLLECTION,
            {"_id": ObjectId(golden_sql.id)},
            golden_sql_dict,
        )
        return golden_sql

    def find_by_id(self, id: str) -> GoldenSQL | None:
        row = self.storage.find_one(DB_COLLECTION, {"_id": ObjectId(id)})
        if not row:
            return None
        row["id"] = str(row["_id"])
        row["db_connection_id"] = str(row["db_connection_id"])
        return GoldenSQL(**row)

    def find_by(self, query: dict, page: int = 1, limit: int = 10) -> list[GoldenSQL]:
        rows = self.storage.find(DB_COLLECTION, query, page=page, limit=limit)
        golden_sqls = []
        for row in rows:
            row["id"] = str(row["_id"])
            row["db_connection_id"] = str(row["db_connection_id"])
            golden_sqls.append(GoldenSQL(**row))
        return golden_sqls

    def find_all(self, page: int = 0, limit: int = 0) -> list[GoldenSQL]:
        rows = self.storage.find_all(DB_COLLECTION, page=page, limit=limit)
        golden_sqls = []
        for row in rows:
            row["id"] = str(row["_id"])
            row["db_connection_id"] = str(row["db_connection_id"])
            golden_sqls.append(GoldenSQL(**row))
        return golden_sqls

    def delete_by_id(self, id: str) -> int:
        return self.storage.delete_by_id(DB_COLLECTION, id)
