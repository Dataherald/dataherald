from typing import Any, List

import fastapi
from fastapi import FastAPI as _FastAPI
from fastapi import status
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute

import dataherald
from dataherald.api.types import Query
from dataherald.config import Settings
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
            "/api/v1/table-descriptions/scan",
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
            "/api/v1/question",
            self.answer_question,
            methods=["POST"],
            tags=["Question"],
        )

        self.router.add_api_route(
            "/api/v1/nl-query-responses",
            self.get_nl_query_response,
            methods=["POST"],
            tags=["NL query responses"],
        )

        self.router.add_api_route(
            "/api/v1/nl-query-responses/{query_id}",
            self.update_nl_query_response,
            methods=["PATCH"],
            tags=["NL query responses"],
        )

        self.router.add_api_route(
            "/api/v1/sql-query-executions",
            self.execute_sql_query,
            methods=["POST"],
            tags=["SQL queries"],
        )

        self.router.add_api_route(
            "/api/v1/heartbeat", self.heartbeat, methods=["GET"], tags=["System"]
        )

        self._app.include_router(self.router)
        use_route_names_as_operation_ids(self._app)

    def app(self) -> fastapi.FastAPI:
        return self._app

    def scan_db(self, scanner_request: ScannerRequest) -> bool:
        return self._api.scan_db(scanner_request)

    def answer_question(self, question_request: QuestionRequest) -> NLQueryResponse:
        return self._api.answer_question(question_request)

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
    ) -> TableSchemaDetail:
        """Add descriptions for tables and columns"""
        return self._api.update_table_description(
            table_description_id, table_description_request
        )

    def list_table_descriptions(
        self, db_connection_id: str | None = None, table_name: str | None = None
    ) -> list[TableSchemaDetail]:
        """List table descriptions"""
        return self._api.list_table_descriptions(db_connection_id, table_name)

    def execute_sql_query(self, query: Query) -> tuple[str, dict]:
        """Executes a query on the given db_connection_id"""
        return self._api.execute_sql_query(query)

    def update_nl_query_response(
        self, query_id: str, query: UpdateQueryRequest
    ) -> NLQueryResponse:
        """Executes a query on the given db_connection_id"""
        return self._api.update_nl_query_response(query_id, query)

    def get_nl_query_response(
        self, query_request: ExecuteTempQueryRequest
    ) -> NLQueryResponse:
        """Executes a query on the given db_connection_id"""
        return self._api.get_nl_query_response(query_request)

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

    def get_golden_records(self, page: int = 1, limit: int = 10) -> List[GoldenRecord]:
        """Gets golden records"""
        return self._api.get_golden_records(page, limit)
