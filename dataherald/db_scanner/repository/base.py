from dataherald.db_scanner.models.types import TableSchemaDetail, ColumnDetail
from typing import List, Optional


class DBScannerRepository:
    def __init__(self, storage):
        self.storage = storage

    def get_table_info(self, db_alias: str, table_name: str) -> Optional[TableSchemaDetail]:
        row = self.storage.find_one(
            "table_schema_detail",
            {"db_alias": db_alias, "table_name": table_name}
        )
        if row:
            return TableSchemaDetail(**row)
        return None

    def get_all_tables_by_db(self, db_alias: str) -> List[TableSchemaDetail]:
        rows = self.storage.find(
            "table_schema_detail",
            {"db_alias": db_alias}
        )
        return [TableSchemaDetail(**row) for row in rows]

    def save_table_info(self, table_info: TableSchemaDetail) -> None:
        self.storage.update_or_create(
            "table_schema_detail",
            {"db_alias": table_info.db_alias, "table_name": table_info.db_alias},
            table_info.dict(),
        )
