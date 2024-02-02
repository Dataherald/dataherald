from bson.objectid import ObjectId
from overrides import override
from pymongo import MongoClient

from dataherald.config import System
from dataherald.db import DB


class MongoDB(DB):
    client: MongoClient

    def __init__(self, system: System):
        super().__init__(system)
        db_uri = system.settings.require("db_uri")
        db_name = system.settings.require("db_name")
        self._data_store = MongoClient(db_uri, tz_aware=True)[db_name]

    @override
    def find_one(self, collection: str, query: dict) -> dict:
        return self._data_store[collection].find_one(query)

    @override
    def insert_one(self, collection: str, obj: dict) -> int:
        return self._data_store[collection].insert_one(obj).inserted_id

    @override
    def rename(self, old_collection_name: str, new_collection_name) -> None:
        self._data_store[old_collection_name].rename(new_collection_name)

    @override
    def rename_field(
        self, collection_name: str, old_field_name: str, new_field_name: str
    ) -> None:
        self._data_store[collection_name].update_many(
            {}, {"$rename": {old_field_name: new_field_name}}
        )

    @override
    def update_or_create(self, collection: str, query: dict, obj: dict) -> int:
        row = self.find_one(collection, query)
        if row:
            if "created_at" in obj:
                del obj["created_at"]
            self._data_store[collection].update_one(query, {"$set": obj})
            return row["_id"]
        return self.insert_one(collection, obj)

    @override
    def find_by_id(self, collection: str, id: str) -> dict:
        return self._data_store[collection].find_one({"_id": ObjectId(id)})

    @override
    def find(
        self,
        collection: str,
        query: dict,
        sort: list = None,
        page: int = 0,
        limit: int = 0,
    ) -> list:
        skip_count = (page - 1) * limit
        cursor = self._data_store[collection].find(query)
        if sort:
            cursor = cursor.sort(sort)
        if page > 0 and limit > 0:
            cursor = cursor.skip(skip_count).limit(limit)
        return list(cursor)

    @override
    def find_all(self, collection: str, page: int = 0, limit: int = 0) -> list:
        if page > 0 and limit > 0:
            skip_count = (page - 1) * limit
            return list(
                self._data_store[collection].find({}).skip(skip_count).limit(limit)
            )
        return list(self._data_store[collection].find({}))

    @override
    def delete_by_id(self, collection: str, id: str) -> int:
        result = self._data_store[collection].delete_one({"_id": ObjectId(id)})
        return result.deleted_count
