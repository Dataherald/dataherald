"""Base class that all cache classes inherit from."""
from abc import ABC, abstractmethod
from typing import Any, Union
from dataherald.sql_database.base import SQLDatabase
from dataherald.db_scanner.repository.base import DBScannerRepository

from dataherald.config import Component


class Scanner(Component, ABC):
    @abstractmethod
    def scan(self, db_engine: SQLDatabase, db_alias: str, repository: DBScannerRepository) -> None:
        """"Scan a db"""
