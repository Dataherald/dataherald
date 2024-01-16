from bson.objectid import ObjectId

from dataherald.sql_database.models.types import DatabaseConnection

DB_COLLECTION = "database_connections"


class DatabaseConnectionNotFoundError(Exception):
    pass


class DatabaseConnectionRepository:
    def __init__(self, storage):
        self.storage = storage

    def insert(self, database_connection: DatabaseConnection) -> DatabaseConnection:
        database_connection.id = str(
            self.storage.insert_one(
                DB_COLLECTION, database_connection.dict(exclude={"id"})
            )
        )
        return database_connection

    def find_one(self, query: dict) -> DatabaseConnection | None:
        row = self.storage.find_one(DB_COLLECTION, query)
        if not row:
            return None
        obj = DatabaseConnection(**row)
        obj.id = str(row["_id"])
        return obj

    def update(self, database_connection: DatabaseConnection) -> DatabaseConnection:
        self.storage.update_or_create(
            DB_COLLECTION,
            {"_id": ObjectId(database_connection.id)},
            database_connection.dict(exclude={"id"}),
        )
        return database_connection

    def find_by_id(self, id: str) -> DatabaseConnection | None:
        row = self.storage.find_one(DB_COLLECTION, {"_id": ObjectId(id)})
        if not row:
            return None
        obj = DatabaseConnection(**row)
        obj.id = str(row["_id"])
        return obj

    def find_all(self) -> list[DatabaseConnection]:
        rows = self.storage.find_all(DB_COLLECTION)
        result = []
        for row in rows:
            obj = DatabaseConnection(**row)
            obj.id = str(row["_id"])
            result.append(obj)
        return result
