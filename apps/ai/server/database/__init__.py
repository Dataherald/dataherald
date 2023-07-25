from abc import ABC, abstractmethod


class DB(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def insert_one(self, collection: str, obj: dict) -> int:
        pass

    @abstractmethod
    def update_or_create(self, collection: str, query: dict, obj: dict) -> int:
        pass

    @abstractmethod
    def find_one(self, collection: str, query: dict) -> dict:
        pass
