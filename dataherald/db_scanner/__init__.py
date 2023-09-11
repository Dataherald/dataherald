"""Base class that all scanner classes inherit from."""
from abc import ABC, abstractmethod
from typing import Any, Union

from dataherald.config import Component
from dataherald.db_scanner.repository.base import DBScannerRepository
from dataherald.sql_database.base import SQLDatabase


class Scanner(Component, ABC):
    @abstractmethod
    def scan(
        self,
        db_engine: SQLDatabase,
        db_connection_id: str,
        table_names: list[str] | None,
        repository: DBScannerRepository,
    ) -> None:
        """ "Scan a db"""
