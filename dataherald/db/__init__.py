from abc import ABC, abstractmethod

from dataherald.config import Component, System


class DB(Component, ABC):
    @abstractmethod
    def __init__(self, system: System):
        self.system = system

    @abstractmethod
    def insert_one(self, collection: str, obj: dict) -> int:
        pass

    @abstractmethod
    def update_or_create(self, collection: str, query: dict, obj: dict) -> int:
        pass

    @abstractmethod
    def find_one(self, collection: str, query: dict) -> dict:
        pass
