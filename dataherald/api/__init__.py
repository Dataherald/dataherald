from abc import ABC, abstractmethod
from typing import List

from fastapi import BackgroundTasks
from fastapi.responses import FileResponse

from dataherald.api.types import Query
from dataherald.config import Component
from dataherald.db_scanner.models.types import QueryHistory, TableDescription
from dataherald.sql_database.models.types import DatabaseConnection, SSHSettings
from dataherald.types import (
    CancelFineTuningRequest,
    CreateResponseRequest,
    DatabaseConnectionRequest,
    Finetuning,
    FineTuningRequest,
    GoldenRecord,
    GoldenRecordRequest,
    Instruction,
    InstructionRequest,
    Question,
    QuestionRequest,
    Response,
    ScannerRequest,
    TableDescriptionRequest,
    UpdateInstruction,
)


class API(Component, ABC):
    @abstractmethod
    def heartbeat(self) -> int:
        """Returns the current server time in nanoseconds to check if the server is alive"""
        pass

    @abstractmethod
    def scan_db(
        self, scanner_request: ScannerRequest, background_tasks: BackgroundTasks
    ) -> bool:
        pass

    @abstractmethod
    def answer_question(
        self,
        run_evaluator: bool = True,
        generate_csv: bool = False,
        question_request: QuestionRequest = None,
    ) -> Response:
        pass

    @abstractmethod
    def answer_question_with_timeout(
        self,
        run_evaluator: bool = True,
        generate_csv: bool = False,
        question_request: QuestionRequest = None,
    ) -> Response:
        pass

    @abstractmethod
    def update_response(self, response_id: str) -> Response:
        pass

    @abstractmethod
    def get_questions(self, db_connection_id: str | None = None) -> list[Question]:
        pass

    @abstractmethod
    def get_question(self, question_id: str) -> Question:
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
    ) -> TableDescription:
        pass

    @abstractmethod
    def list_table_descriptions(
        self, db_connection_id: str, table_name: str | None = None
    ) -> list[TableDescription]:
        pass

    @abstractmethod
    def get_table_description(self, table_description_id: str) -> TableDescription:
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
    def create_response(
        self,
        run_evaluator: bool = True,
        sql_response_only: bool = False,
        generate_csv: bool = False,
        query_request: CreateResponseRequest = None,
    ) -> Response:
        pass

    @abstractmethod
    def get_query_history(self, db_connection_id: str) -> list[QueryHistory]:
        pass

    @abstractmethod
    def get_responses(self, question_id: str | None = None) -> list[Response]:
        pass

    @abstractmethod
    def get_response(self, response_id: str) -> Response:
        pass

    @abstractmethod
    def get_response_file(
        self, response_id: str, background_tasks: BackgroundTasks
    ) -> FileResponse:
        pass

    @abstractmethod
    def delete_golden_record(self, golden_record_id: str) -> dict:
        pass

    @abstractmethod
    def get_golden_records(
        self, db_connection_id: str = None, page: int = 1, limit: int = 10
    ) -> List[GoldenRecord]:
        pass

    @abstractmethod
    def add_instruction(self, instruction_request: InstructionRequest) -> Instruction:
        pass

    @abstractmethod
    def get_instructions(
        self, db_connection_id: str = None, page: int = 1, limit: int = 10
    ) -> List[Instruction]:
        pass

    @abstractmethod
    def delete_instruction(self, instruction_id: str) -> dict:
        pass

    @abstractmethod
    def update_instruction(
        self,
        instruction_id: str,
        instruction_request: UpdateInstruction,
    ) -> Instruction:
        pass

    @abstractmethod
    def create_finetuning_job(
        self, fine_tuning_request: FineTuningRequest, background_tasks: BackgroundTasks
    ) -> Finetuning:
        pass

    @abstractmethod
    def cancel_finetuning_job(
        self, cancel_fine_tuning_request: CancelFineTuningRequest
    ) -> Finetuning:
        pass

    @abstractmethod
    def get_finetuning_job(self, finetuning_job_id: str) -> Finetuning:
        pass
