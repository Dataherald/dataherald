import pymongo
from bson.objectid import ObjectId
from pymongo.command_cursor import CommandCursor
from pymongo.cursor import Cursor

from config import db_settings

ASCENDING = pymongo.ASCENDING
DESCENDING = pymongo.DESCENDING


class MongoDB:
    db_uri = db_settings.mongodb_uri
    db_name = db_settings.mongodb_db_name
    _data_store = pymongo.MongoClient(db_uri, tz_aware=True)[db_name]

    @classmethod
    def find_one(cls, collection: str, query: dict, sort: list = None) -> dict:
        return cls._data_store[collection].find_one(query, sort=sort)

    @classmethod
    def insert_one(cls, collection: str, obj: dict) -> ObjectId:
        return cls._data_store[collection].insert_one(obj).inserted_id

    @classmethod
    def insert_many(cls, collection: str, objs: list[dict]) -> list[ObjectId]:
        return cls._data_store[collection].insert_many(objs).inserted_ids

    @classmethod
    def update_one(cls, collection: str, query: dict, obj: dict) -> int:
        return (
            cls._data_store[collection].update_one(query, {"$set": obj}).matched_count
        )

    @classmethod
    def update_many(cls, collection: str, filter: dict, obj: dict) -> int:
        return (
            cls._data_store[collection].update_many(filter, {"$set": obj}).matched_count
        )

    @classmethod
    def find_by_id(cls, collection: str, id: str) -> dict:
        return cls._data_store[collection].find_one({"_id": ObjectId(id)})

    @classmethod
    def find_by_object_id(cls, collection: str, id: ObjectId) -> dict:
        return cls._data_store[collection].find_one({"_id": id})

    @classmethod
    def find_by_object_ids(cls, collection: str, ids: list[ObjectId]) -> Cursor:
        return cls._data_store[collection].find({"_id": {"$in": ids}})

    @classmethod
    def find(cls, collection: str, query: dict) -> Cursor:
        return cls._data_store[collection].find(query)

    @classmethod
    def delete_one(cls, collection: str, query: dict) -> int:
        return cls._data_store[collection].delete_one(query).deleted_count

    @classmethod
    def aggregate(cls, collection: str, pipeline: list) -> CommandCursor:
        return cls._data_store[collection].aggregate(pipeline)
