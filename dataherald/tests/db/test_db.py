from overrides import override

from dataherald.config import System
from dataherald.db import DB


class TestDB(DB):
    memory: dict = {}

    def __init__(self, system: System):
        super().__init__(system)
        self.memory = {}
        self.memory["database_connection"] = [
            {"alias": "foo", "use_ssh": False, "uri": "bar", "ssh_settings": None}
        ]

    @override
    def insert_one(self, collection: str, obj: dict) -> int:
        if collection in self.memory:
            self.memory[collection].append(obj)
        else:
            self.memory[collection] = [obj]

        return len(self.memory[collection]) - 1

    @override
    def find_one(self, collection: str, query: dict) -> dict:  # noqa: ARG002
        if collection in self.memory:
            return self.memory[collection][0]
        return {}

    def find_by_id(self, collection: str, id: str) -> dict:
        try:
            collection = self.memory[collection]
        except KeyError:
            return {}

        for item in collection:
            if item.get("_id") == id:
                return item
        return None
