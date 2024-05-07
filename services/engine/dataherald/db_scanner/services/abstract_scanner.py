from abc import ABC, abstractmethod

from sqlalchemy.sql.schema import Column

from dataherald.db_scanner.models.types import QueryHistory
from dataherald.sql_database.base import SQLDatabase


class AbstractScanner(ABC):
    @abstractmethod
    def cardinality_values(self, column: Column, db_engine: SQLDatabase) -> list | None:
        """Returns a list if it is a catalog otherwise return None"""
        pass

    @abstractmethod
    def get_logs(
        self, table: str, db_engine: SQLDatabase, db_connection_id: str
    ) -> list[QueryHistory]:
        """Returns a list of logs"""
        pass
