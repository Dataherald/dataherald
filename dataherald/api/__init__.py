from abc import ABC, abstractmethod
from typing import Any, List

from dataherald.api.types import Query
from dataherald.config import Component
from dataherald.eval import Evaluation
from dataherald.sql_database.models.types import SSHSettings
from dataherald.types import (
    DatabaseConnectionRequest,
    ExecuteTempQueryRequest,
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
    def connect_database(
        self, database_connection_request: DatabaseConnectionRequest
    ) -> bool:
        pass

    @abstractmethod
    def add_description(
        self,
        db_name: str,
        table_name: str,
        table_description_request: TableDescriptionRequest,
    ) -> bool:
        pass

    @abstractmethod
    def add_golden_records(self, golden_records: List) -> bool:
        pass

    @abstractmethod
    def execute_query(self, query: Query) -> tuple[str, dict]:
        pass

    @abstractmethod
    def update_query(self, query_id: str, query: UpdateQueryRequest) -> NLQueryResponse:
        pass

    @abstractmethod
    def execute_temp_query(
        self, query_id: str, query: ExecuteTempQueryRequest
    ) -> NLQueryResponse:
        pass
