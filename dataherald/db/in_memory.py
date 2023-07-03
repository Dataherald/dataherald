from overrides import override

from dataherald.config import System
from dataherald.db import DB


class InMemory(DB):
    memory: dict = {}

    def __init__(self, system: System):
        super().__init__(system)
        self.memory = {}

    @override
    def insert_one(self, collection: str, obj: dict) -> int:
        if collection in self.memory:
            self.memory[collection].append(obj)
        else:
            self.memory[collection] = [obj]

        return len(self.memory[collection]) - 1
