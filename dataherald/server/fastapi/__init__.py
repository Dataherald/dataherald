from typing import Any, List

import fastapi
from fastapi import BackgroundTasks, status
from fastapi import FastAPI as _FastAPI
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute

import dataherald
from dataherald.api.types import Query
from dataherald.config import Settings
from dataherald.db_scanner.models.types import TableDescription
from dataherald.sql_database.models.types import DatabaseConnection, SSHSettings
from dataherald.types import (
    CreateResponseRequest,
    DatabaseConnectionRequest,
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


def use_route_names_as_operation_ids(app: _FastAPI) -> None:
    """
    Simplify operation IDs so that generated API clients have simpler function
    names.
    Should be called only after all routes have been added.
    """
    for route in app.routes:
        if isinstance(route, APIRoute):
            route.operation_id = route.name


class FastAPI(dataherald.server.Server):
    def __init__(self, settings: Settings):
        super().__init__(settings)
        self._app = fastapi.FastAPI(debug=True)
        self._api: dataherald.api.API = dataherald.client(settings)

        self.router = fastapi.APIRouter()

        self.router.add_api_route(
            "/api/v1/database-connections",
            self.create_database_connection,
            methods=["POST"],
            tags=["Database connections"],
        )

        self.router.add_api_route(
            "/api/v1/database-connections",
            self.list_database_connections,
            methods=["GET"],
            tags=["Database connections"],
        )

        self.router.add_api_route(
            "/api/v1/database-connections/{db_connection_id}",
            self.update_database_connection,
            methods=["PUT"],
            tags=["Database connections"],
        )

        self.router.add_api_route(
            "/api/v1/table-descriptions/sync-schemas",
            self.scan_db,
            methods=["POST"],
            tags=["Table descriptions"],
        )

        self.router.add_api_route(
            "/api/v1/table-descriptions/{table_description_id}",
            self.update_table_description,
            methods=["PATCH"],
            tags=["Table descriptions"],
        )

        self.router.add_api_route(
            "/api/v1/table-descriptions",
            self.list_table_descriptions,
            methods=["GET"],
            tags=["Table descriptions"],
        )

        self.router.add_api_route(
            "/api/v1/table-descriptions/{table_description_id}",
            self.get_table_description,
            methods=["GET"],
            tags=["Table descriptions"],
        )

        self.router.add_api_route(
            "/api/v1/golden-records/{golden_record_id}",
            self.delete_golden_record,
            methods=["DELETE"],
            tags=["Golden records"],
        )

        self.router.add_api_route(
            "/api/v1/golden-records",
            self.add_golden_records,
            methods=["POST"],
            tags=["Golden records"],
        )

        self.router.add_api_route(
            "/api/v1/golden-records",
            self.get_golden_records,
            methods=["GET"],
            tags=["Golden records"],
        )

        self.router.add_api_route(
            "/api/v1/questions",
            self.answer_question,
            methods=["POST"],
            tags=["Questions"],
        )

        self.router.add_api_route(
            "/api/v1/questions",
            self.get_questions,
            methods=["GET"],
            tags=["Questions"],
        )

        self.router.add_api_route(
            "/api/v1/questions/{question_id}",
            self.get_question,
            methods=["GET"],
            tags=["Questions"],
        )

        self.router.add_api_route(
            "/api/v1/responses",
            self.create_response,
            methods=["POST"],
            tags=["Responses"],
        )

        self.router.add_api_route(
            "/api/v1/responses",
            self.get_responses,
            methods=["GET"],
            tags=["Responses"],
        )

        self.router.add_api_route(
            "/api/v1/responses/{response_id}",
            self.get_response,
            methods=["GET"],
            tags=["Responses"],
        )

        self.router.add_api_route(
            "/api/v1/sql-query-executions",
            self.execute_sql_query,
            methods=["POST"],
            tags=["SQL queries"],
        )

        self.router.add_api_route(
            "/api/v1/instructions",
            self.add_instruction,
            methods=["POST"],
            tags=["Instructions"],
        )

        self.router.add_api_route(
            "/api/v1/instructions",
            self.get_instructions,
            methods=["GET"],
            tags=["Instructions"],
        )

        self.router.add_api_route(
            "/api/v1/instructions/{instruction_id}",
            self.delete_instruction,
            methods=["DELETE"],
            tags=["Instructions"],
        )

        self.router.add_api_route(
            "/api/v1/instructions/{instruction_id}",
            self.update_instruction,
            methods=["PUT"],
            tags=["Instructions"],
        )

        self.router.add_api_route(
            "/api/v1/heartbeat", self.heartbeat, methods=["GET"], tags=["System"]
        )

        self._app.include_router(self.router)
        use_route_names_as_operation_ids(self._app)

    def app(self) -> fastapi.FastAPI:
        return self._app

    def scan_db(
        self, scanner_request: ScannerRequest, background_tasks: BackgroundTasks
    ) -> bool:
        return self._api.scan_db(scanner_request, background_tasks)

    def answer_question(self, question_request: QuestionRequest) -> Response:
        return self._api.answer_question(question_request)

    def get_questions(self, db_connection_id: str | None = None) -> list[Question]:
        return self._api.get_questions(db_connection_id)

    def get_question(self, question_id: str) -> Question:
        """Get a question"""
        return self._api.get_question(question_id)

    def root(self) -> dict[str, int]:
        return {"nanosecond heartbeat": self._api.heartbeat()}

    def heartbeat(self) -> dict[str, int]:
        return self.root()

    def create_database_connection(
        self, database_connection_request: DatabaseConnectionRequest
    ) -> DatabaseConnection:
        """Creates a database connection"""
        return self._api.create_database_connection(database_connection_request)

    def list_database_connections(self) -> list[DatabaseConnection]:
        """List all database connections"""
        return self._api.list_database_connections()

    def update_database_connection(
        self,
        db_connection_id: str,
        database_connection_request: DatabaseConnectionRequest,
    ) -> DatabaseConnection:
        """Creates a database connection"""
        return self._api.update_database_connection(
            db_connection_id, database_connection_request
        )

    def update_table_description(
        self,
        table_description_id: str,
        table_description_request: TableDescriptionRequest,
    ) -> TableDescription:
        """Add descriptions for tables and columns"""
        return self._api.update_table_description(
            table_description_id, table_description_request
        )

    def list_table_descriptions(
        self, db_connection_id: str, table_name: str | None = None
    ) -> list[TableDescription]:
        """List table descriptions"""
        return self._api.list_table_descriptions(db_connection_id, table_name)

    def get_table_description(self, table_description_id: str) -> TableDescription:
        """Get description"""
        return self._api.get_table_description(table_description_id)

    def get_responses(self, question_id: str | None = None) -> list[Response]:
        """List responses"""
        return self._api.get_responses(question_id)

    def get_response(self, response_id: str) -> Response:
        """Get a response"""
        return self._api.get_response(response_id)

    def execute_sql_query(self, query: Query) -> tuple[str, dict]:
        """Executes a query on the given db_connection_id"""
        return self._api.execute_sql_query(query)

    def create_response(self, query_request: CreateResponseRequest) -> Response:
        """Executes a query on the given db_connection_id"""
        return self._api.create_response(query_request)

    def delete_golden_record(self, golden_record_id: str) -> dict:
        """Deletes a golden record"""
        return self._api.delete_golden_record(golden_record_id)

    def add_golden_records(
        self, golden_records: List[GoldenRecordRequest]
    ) -> List[GoldenRecord]:
        created_records = self._api.add_golden_records(golden_records)

        # Return a JSONResponse with status code 201 and the location header.
        golden_records_as_dicts = [record.dict() for record in created_records]

        return JSONResponse(
            content=golden_records_as_dicts, status_code=status.HTTP_201_CREATED
        )

    def get_golden_records(
        self, db_connection_id: str = None, page: int = 1, limit: int = 10
    ) -> List[GoldenRecord]:
        """Gets golden records"""
        return self._api.get_golden_records(db_connection_id, page, limit)

    def add_instruction(self, instruction_request: InstructionRequest) -> Instruction:
        """Adds an instruction"""
        created_records = self._api.add_instruction(instruction_request)

        # Return a JSONResponse with status code 201 and the location header.
        instruction_as_dict = created_records.dict()

        return JSONResponse(
            content=instruction_as_dict, status_code=status.HTTP_201_CREATED
        )

    def get_instructions(
        self, db_connection_id: str = None, page: int = 1, limit: int = 10
    ) -> List[Instruction]:
        """Gets instructions"""
        return self._api.get_instructions(db_connection_id, page, limit)

    def delete_instruction(self, instruction_id: str) -> dict:
        """Deletes an instruction"""
        return self._api.delete_instruction(instruction_id)

    def update_instruction(
        self,
        instruction_id: str,
        instruction_request: UpdateInstruction,
    ) -> Instruction:
        """Updates an instruction"""
        return self._api.update_instruction(instruction_id, instruction_request)
