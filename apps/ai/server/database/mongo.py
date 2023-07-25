from bson.objectid import ObjectId
from overrides import override
from pymongo import MongoClient
from pymongo.cursor import Cursor

from config import MONGODB_DB_NAME, MONGODB_URI
from database import DB


class MongoDB(DB):
    def __init__(self):
        self.db_uri = MONGODB_URI
        self.db_name = MONGODB_DB_NAME
        self._data_store = MongoClient(self.db_uri)[self.db_name]

    @override
    def find_one(self, collection: str, query: dict) -> dict:
        return self._data_store[collection].find_one(query)

    @override
    def insert_one(self, collection: str, obj: dict) -> int:
        return self._data_store[collection].insert_one(obj).inserted_id

    @override
    def update_or_create(self, collection: str, query: dict, obj: dict) -> int:
        row = self.find_one(collection, query)
        if row:
            return self._data_store[collection].update_one(query, {"$set": obj})
        return self.insert_one(collection, obj)

    def find_by_id(self, collection: str, id: str) -> dict:
        return self._data_store[collection].find_one({"_id": ObjectId(id)})

    def find(self, collection: str, query: dict) -> Cursor:
        return self._data_store[collection].find(query)
