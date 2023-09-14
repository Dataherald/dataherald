from abc import ABC, abstractmethod
from typing import List

from dataherald.api.types import Query
from dataherald.config import Component
from dataherald.db_scanner.models.types import TableSchemaDetail
from dataherald.sql_database.models.types import DatabaseConnection, SSHSettings
from dataherald.types import (
    DatabaseConnectionRequest,
    ExecuteTempQueryRequest,
    GoldenRecord,
    GoldenRecordRequest,
    NLQueryResponse,
    QuestionRequest,
    ScannerRequest,
    TableDescriptionRequest,
    UpdateQueryRequest,
)


class API(Component, ABC):
    @abstractmethod
    def heartbeat(self) -> int:
        """Returns the current server time in nanoseconds to check if the server is alive"""
        pass

    @abstractmethod
    def scan_db(self, scanner_request: ScannerRequest) -> bool:
        pass

    @abstractmethod
    def answer_question(self, question_request: QuestionRequest) -> NLQueryResponse:
        pass

    @abstractmethod
    def create_database_connection(
        self, database_connection_request: DatabaseConnectionRequest
    ) -> DatabaseConnection:
        pass

    @abstractmethod
    def list_database_connections(self) -> list[DatabaseConnection]:
        pass

    @abstractmethod
    def update_database_connection(
        self,
        db_connection_id: str,
        database_connection_request: DatabaseConnectionRequest,
    ) -> DatabaseConnection:
        pass

    @abstractmethod
    def update_table_description(
        self,
        table_description_id: str,
        table_description_request: TableDescriptionRequest,
    ) -> TableSchemaDetail:
        pass

    @abstractmethod
    def list_table_descriptions(
        self, db_connection_id: str | None = None, table_name: str | None = None
    ) -> list[TableSchemaDetail]:
        pass

    @abstractmethod
    def add_golden_records(
        self, golden_records: List[GoldenRecordRequest]
    ) -> List[GoldenRecord]:
        pass

    @abstractmethod
    def execute_sql_query(self, query: Query) -> tuple[str, dict]:
        pass

    @abstractmethod
    def update_nl_query_response(
        self, query_id: str, query: UpdateQueryRequest
    ) -> NLQueryResponse:
        pass

    @abstractmethod
    def get_nl_query_response(
        self, query_request: ExecuteTempQueryRequest
    ) -> NLQueryResponse:
        pass

    @abstractmethod
    def delete_golden_record(self, golden_record_id: str) -> dict:
        pass

    @abstractmethod
    def get_golden_records(self, page: int = 1, limit: int = 10) -> List[GoldenRecord]:
        pass
