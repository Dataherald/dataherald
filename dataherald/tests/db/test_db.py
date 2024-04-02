from bson.objectid import ObjectId
from overrides import override

from dataherald.config import System
from dataherald.db import DB


class TestDB(DB):
    memory: dict = {}

    def __init__(self, system: System):
        super().__init__(system)
        self.memory = {}
        self.memory["database_connections"] = [
            {
                "_id": ObjectId("64dfa0e103f5134086f7090c"),
                "alias": "alias",
                "use_ssh": False,
                "connection_uri": "gAAAAABkwD9Y9EpBxF1hRxhovjvedX1TeDNu-WaGqDebk_CJnpGjRlpXzDOl_puehMSbz9KDQ6OqPepl8XQpD0EchiV7he4j5tEXYE33eak87iORA7s8ko0=",  # noqa: E501
                "ssh_settings": None,
            }
        ]
        self.memory["instructions"] = [
            {
                "_id": ObjectId("64dfa0e103f5134086f7090c"),
                "instruction": "foo",
                "db_connection_id": "64dfa0e103f5134086f7090c",
            }
        ]

    @override
    def insert_one(self, collection: str, obj: dict) -> int:
        obj["_id"] = ObjectId("651f2d76275132d5b65175eb")
        if collection in self.memory:
            self.memory[collection].append(obj)
        else:
            self.memory[collection] = [obj]

        return ObjectId("651f2d76275132d5b65175eb")

    @override
    def find_one(self, collection: str, query: dict) -> dict:  # noqa: ARG002
        if collection in self.memory:
            return self.memory[collection][0]
        return {}

    @override
    def find_by_id(self, collection: str, id: str) -> dict:
        try:
            collection = self.memory[collection]
        except KeyError:
            return {}

        for item in collection:
            if item.get("_id") == id:
                return item
        return None

    @override
    def find(
        self,
        collection: str,
        query: dict,
        sort: list = None,
        page: int = 0,
        limit: int = 0,
    ) -> list:
        return []

    @override
    def update_or_create(self, collection: str, query: dict, obj: dict) -> int:
        return self.insert_one(collection, obj)

    @override
    def find_all(self, collection: str, page: int = 0, limit: int = 0) -> list:
        return self.memory[collection]

    @override
    def delete_by_id(self, collection: str, id: str) -> int:
        try:
            collection = self.memory[collection]
        except KeyError:
            return 0

        for i, item in enumerate(collection):
            if item.get("_id") == id:
                del collection[i]
                return 1
        return 0

    @override
    def rename(self, old_collection_name: str, new_collection_name) -> None:
        pass

    @override
    def rename_field(
        self, collection_name: str, old_field_name: str, new_field_name: str
    ) -> None:
        pass
