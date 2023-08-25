from typing import List

from bson.objectid import ObjectId

from dataherald.db_scanner.models.types import TableSchemaDetail

DB_COLLECTION = "table_schema_detail"


class DBScannerRepository:
    def __init__(self, storage):
        self.storage = storage

    def get_table_info(
        self, db_alias: str, table_name: str
    ) -> TableSchemaDetail | None:
        row = self.storage.find_one(
            DB_COLLECTION, {"db_alias": db_alias, "table_name": table_name}
        )
        if row:
            row["id"] = row["_id"]
            return TableSchemaDetail(**row)
        return None

    def get_all_tables_by_db(self, db_alias: str) -> List[TableSchemaDetail]:
        rows = self.storage.find(DB_COLLECTION, {"db_alias": db_alias})
        tables = []
        for row in rows:
            row["id"] = row["_id"]
            tables.append(TableSchemaDetail(**row))
        return tables

    def save_table_info(self, table_info: TableSchemaDetail) -> None:
        self.storage.update_or_create(
            DB_COLLECTION,
            {"db_alias": table_info.db_alias, "table_name": table_info.table_name},
            table_info.dict(),
        )

    def update(self, table_info: TableSchemaDetail) -> TableSchemaDetail:
        self.storage.update_or_create(
            DB_COLLECTION,
            {"_id": ObjectId(table_info.id)},
            table_info.dict(exclude={"id"}),
        )
        return table_info
