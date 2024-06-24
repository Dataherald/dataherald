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
        table_descriptions: list[TableDescription],
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
    def create_tables(
        self,
        tables: list[str],
        db_connection_id: str,
        schema: str,
        repository: TableDescriptionRepository,
        metadata: dict = None,
    ) -> None:
        """ "Create tables"""

    @abstractmethod
    def refresh_tables(
        self,
        schemas_and_tables: dict[str, list],
        db_connection_id: str,
        repository: TableDescriptionRepository,
        metadata: dict = None,
    ) -> list[TableDescription]:
        """ "Refresh tables"""
