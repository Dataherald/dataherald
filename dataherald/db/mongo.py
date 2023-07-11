from overrides import override
from pymongo import MongoClient

from dataherald.config import System
from dataherald.db import DB


class MongoDB(DB):
    client: MongoClient

    def __init__(self, system: System):
        super().__init__(system)
        db_host = system.settings.require("db_host")
        db_port = system.settings.require("db_port")
        db_username = system.settings.require("db_username")
        db_password = system.settings.require("db_password")
        db_name = system.settings.require("db_name")
        connection_url: str = (
            f"mongodb+srv://{db_username}:{db_password}@{db_host}/?retryWrites=true"
        )
        self._data_store = MongoClient(connection_url)[db_name]

    @override
    def find_one(self, collection: str, query: dict) -> dict:
        return self._data_store[collection].find_one(query)

    @override
    def insert_one(self, collection: str, obj: dict) -> int:
        return self._data_store[collection].insert_one(obj).inserted_id
