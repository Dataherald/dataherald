from bson.objectid import ObjectId
from pymongo import MongoClient
from pymongo.cursor import Cursor

from config import dbsettings


class MongoDB:
    db_uri = dbsettings.mongodb_uri
    db_name = dbsettings.mongodb_db_name
    _data_store = MongoClient(db_uri)[db_name]

    @classmethod
    def find_one(cls, collection: str, query: dict) -> dict:
        return cls._data_store[collection].find_one(query)

    @classmethod
    def insert_one(cls, collection: str, obj: dict) -> int:
        return cls._data_store[collection].insert_one(obj).inserted_id

    @classmethod
    def update_or_create(cls, collection: str, query: dict, obj: dict) -> int:
        row = cls.find_one(collection, query)
        if row:
            return cls._data_store[collection].update_one(query, {"$set": obj})
        return cls.insert_one(collection, obj)

    @classmethod
    def find_by_id(cls, collection: str, id: ObjectId) -> dict:
        return cls._data_store[collection].find_one({"_id": id})

    @classmethod
    def find_by_object_id(cls, collection: str, id: str) -> dict:
        return cls._data_store[collection].find_one({"_id": ObjectId(id)})

    @classmethod
    def find_by_object_ids(cls, collection: str, ids: list[ObjectId]) -> Cursor:
        return cls._data_store[collection].find({"_id": {"$in": ids}})

    @classmethod
    def find(cls, collection: str, query: dict) -> Cursor:
        return cls._data_store[collection].find(query)
