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
    def rename(self, old_collection_name: str, new_collection_name) -> None:
        pass

    @abstractmethod
    def rename_field(
        self, collection_name: str, old_field_name: str, new_field_name: str
    ) -> None:
        pass

    @abstractmethod
    def update_or_create(self, collection: str, query: dict, obj: dict) -> int:
        pass

    @abstractmethod
    def find_one(self, collection: str, query: dict) -> dict:
        pass

    @abstractmethod
    def find_by_id(self, collection: str, id: str) -> dict:
        pass

    @abstractmethod
    def find(
        self,
        collection: str,
        query: dict,
        sort: list = None,
        page: int = 0,
        limit: int = 0,
    ) -> list:
        pass

    @abstractmethod
    def find_all(self, collection: str, page: int = 0, limit: int = 0) -> list:
        pass

    @abstractmethod
    def delete_by_id(self, collection: str, id: str) -> int:
        pass
