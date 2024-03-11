from typing import List

from bson.objectid import ObjectId
from pymongo import ASCENDING

from dataherald.db_scanner.models.types import TableDescription

DB_COLLECTION = "table_descriptions"


class InvalidColumnNameError(Exception):
    pass


class TableDescriptionRepository:
    def __init__(self, storage):
        self.storage = storage

    def find_by_id(self, id: str) -> TableDescription | None:
        row = self.storage.find_one(DB_COLLECTION, {"_id": ObjectId(id)})
        if not row:
            return None
        row["id"] = str(row["_id"])
        row["db_connection_id"] = str(row["db_connection_id"])
        return TableDescription(**row)

    def get_table_info(
        self, db_connection_id: str, table_name: str
    ) -> TableDescription | None:
        row = self.storage.find_one(
            DB_COLLECTION,
            {"db_connection_id": str(db_connection_id), "table_name": table_name},
        )
        if row:
            row["id"] = str(row["_id"])
            row["db_connection_id"] = str(row["db_connection_id"])
            return TableDescription(**row)
        return None

    def get_all_tables_by_db(self, query: dict) -> List[TableDescription]:
        rows = self.storage.find(DB_COLLECTION, query)
        tables = []
        for row in rows:
            row["id"] = str(row["_id"])
            row["db_connection_id"] = str(row["db_connection_id"])
            tables.append(TableDescription(**row))
        return tables

    def save_table_info(self, table_info: TableDescription) -> TableDescription:
        table_info_dict = table_info.dict(exclude={"id"})
        table_info_dict["db_connection_id"] = str(table_info.db_connection_id)
        table_info_dict["table_name"] = table_info.table_name.lower()
        table_info_dict = {
            k: v for k, v in table_info_dict.items() if v is not None and v != []
        }
        table_info.id = str(
            self.storage.update_or_create(
                DB_COLLECTION,
                {
                    "db_connection_id": table_info_dict["db_connection_id"],
                    "table_name": table_info_dict["table_name"],
                },
                table_info_dict,
            )
        )
        return table_info

    def update(self, table_info: TableDescription) -> TableDescription:
        table_info_dict = table_info.dict(exclude={"id"})
        table_info_dict["db_connection_id"] = str(table_info.db_connection_id)
        table_info_dict = {
            k: v for k, v in table_info_dict.items() if v is not None and v != []
        }
        self.storage.update_or_create(
            DB_COLLECTION,
            {"_id": ObjectId(table_info.id)},
            table_info_dict,
        )
        return table_info

    def find_all(self) -> list[TableDescription]:
        rows = self.storage.find_all(DB_COLLECTION)
        result = []
        for row in rows:
            row["id"] = str(row["_id"])
            row["db_connection_id"] = str(row["db_connection_id"])
            obj = TableDescription(**row)
            result.append(obj)
        return result

    def find_by(self, query: dict) -> list[TableDescription]:
        query = {k: v for k, v in query.items() if v}
        rows = self.storage.find(DB_COLLECTION, query, sort=[("table_name", ASCENDING)])
        result = []
        for row in rows:
            row["id"] = str(row["_id"])
            row["db_connection_id"] = str(row["db_connection_id"])
            obj = TableDescription(**row)
            obj.columns = sorted(obj.columns, key=lambda x: x.name)
            result.append(obj)
        return result

    def update_fields(self, table: TableDescription, table_description_request):
        if table_description_request.description is not None:
            table.description = table_description_request.description

        if table_description_request.metadata is not None:
            table.metadata = table_description_request.metadata

        if table_description_request.columns:
            columns = [column.name for column in table.columns]

            for column_request in table_description_request.columns:
                if column_request.name not in columns:
                    raise InvalidColumnNameError(
                        f"Column {column_request.name} doesn't exist"
                    )
                for column in table.columns:
                    if column_request.name == column.name:
                        for field, value in column_request:
                            if value is None or value == []:
                                continue
                            setattr(column, field, value)
        return self.update(table)
