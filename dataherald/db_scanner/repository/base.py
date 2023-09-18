from typing import List

from bson.objectid import ObjectId
from pymongo import ASCENDING

from dataherald.db_scanner.models.types import TableSchemaDetail

DB_COLLECTION = "table_descriptions"


class DBScannerRepository:
    def __init__(self, storage):
        self.storage = storage

    def find_by_id(self, id: str) -> TableSchemaDetail | None:
        row = self.storage.find_one(DB_COLLECTION, {"_id": ObjectId(id)})
        if not row:
            return None
        obj = TableSchemaDetail(**row)
        obj.id = str(row["_id"])
        return obj

    def get_table_info(
        self, db_connection_id: str, table_name: str
    ) -> TableSchemaDetail | None:
        row = self.storage.find_one(
            DB_COLLECTION,
            {"db_connection_id": db_connection_id, "table_name": table_name},
        )
        if row:
            row["id"] = row["_id"]
            return TableSchemaDetail(**row)
        return None

    def get_all_tables_by_db(self, db_connection_id: str) -> List[TableSchemaDetail]:
        rows = self.storage.find(DB_COLLECTION, {"db_connection_id": db_connection_id})
        tables = []
        for row in rows:
            row["id"] = row["_id"]
            tables.append(TableSchemaDetail(**row))
        return tables

    def save_table_info(self, table_info: TableSchemaDetail) -> None:
        self.storage.update_or_create(
            DB_COLLECTION,
            {
                "db_connection_id": table_info.db_connection_id,
                "table_name": table_info.table_name,
            },
            table_info.dict(),
        )

    def update(self, table_info: TableSchemaDetail) -> TableSchemaDetail:
        self.storage.update_or_create(
            DB_COLLECTION,
            {"_id": ObjectId(table_info.id)},
            table_info.dict(exclude={"id"}),
        )
        return table_info

    def find_all(self) -> list[TableSchemaDetail]:
        rows = self.storage.find_all(DB_COLLECTION)
        result = []
        for row in rows:
            obj = TableSchemaDetail(**row)
            obj.id = str(row["_id"])
            result.append(obj)
        return result

    def find_by(self, query: dict) -> list[TableSchemaDetail]:
        query = {k: v for k, v in query.items() if v}
        rows = self.storage.find(DB_COLLECTION, query, sort=[("table_name", ASCENDING)])
        result = []
        for row in rows:
            obj = TableSchemaDetail(**row)
            obj.columns = sorted(obj.columns, key=lambda x: x.name)
            obj.id = str(row["_id"])
            result.append(obj)
        return result
