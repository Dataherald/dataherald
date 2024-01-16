"""Base class that all scanner classes inherit from."""
from abc import ABC, abstractmethod

from dataherald.config import Component
from dataherald.db_scanner.models.types import TableDescription
from dataherald.db_scanner.repository.base import TableDescriptionRepository
from dataherald.db_scanner.repository.query_history import QueryHistoryRepository
from dataherald.sql_database.base import SQLDatabase
from dataherald.types import ScannerRequest


class Scanner(Component, ABC):
    @abstractmethod
    def scan(
        self,
        db_engine: SQLDatabase,
        db_connection_id: str,
        table_names: list[str] | None,
        repository: TableDescriptionRepository,
        query_history_repository: QueryHistoryRepository,
    ) -> None:
        """ "Scan a db"""

    @abstractmethod
    def synchronizing(
        self,
        scanner_request: ScannerRequest,
        repository: TableDescriptionRepository,
    ) -> list[TableDescription]:
        """ "Update table_description status"""

    @abstractmethod
    def get_all_tables_and_views(self, database: SQLDatabase) -> list[str]:
        """ "Retrieve all tables and views"""
