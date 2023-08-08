from typing import Any, List

import fastapi
from fastapi import FastAPI as _FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute

import dataherald
from dataherald.api.types import Query
from dataherald.config import Settings
from dataherald.eval import Evaluation
from dataherald.sql_database.models.types import DatabaseConnection, SSHSettings
from dataherald.types import (
    DatabaseConnectionRequest,
    DataDefinitionRequest,
    EvaluationRequest,
    ExecuteTempQueryRequest,
    NLQueryResponse,
    QuestionRequest,
    ScannerRequest,
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
            "/api/v1/question", self.answer_question, methods=["POST"]
        )

        self.router.add_api_route("/api/v1/scanner", self.scan_db, methods=["POST"])

        self.router.add_api_route(
            "/api/v1/question/evaluate", self.evaluate_question, methods=["POST"]
        )

        self.router.add_api_route("/api/v1/heartbeat", self.heartbeat, methods=["GET"])

        self.router.add_api_route(
            "/api/v1/database", self.connect_database, methods=["POST"]
        )

        self.router.add_api_route(
            "/api/v1/golden-record", self.add_golden_records, methods=["POST"]
        )

        self.router.add_api_route(
            "/api/v1/data-definition", self.add_data_definition, methods=["POST"]
        )

        self.router.add_api_route("/api/v1/query", self.execute_query, methods=["POST"])

        self.router.add_api_route(
            "/api/v1/query/{query_id}", self.update_query, methods=["PATCH"]
        )

        self.router.add_api_route(
            "/api/v1/query/{query_id}/execution",
            self.execute_temp_query,
            methods=["POST"],
        )

        self._app.include_router(self.router)
        use_route_names_as_operation_ids(self._app)

    def app(self) -> fastapi.FastAPI:
        return self._app

    def scan_db(self, scanner_request: ScannerRequest) -> bool:
        return self._api.scan_db(scanner_request)

    def answer_question(self, question_request: QuestionRequest) -> NLQueryResponse:
        return self._api.answer_question(question_request)

    def evaluate_question(self, evaluation_request: EvaluationRequest) -> Evaluation:
        return self._api.evaluate(evaluation_request)

    def root(self) -> dict[str, int]:
        return {"nanosecond heartbeat": self._api.heartbeat()}

    def heartbeat(self) -> dict[str, int]:
        return self.root()

    def connect_database(
        self, database_connection_request: DatabaseConnectionRequest
    ) -> bool:
        """Connects a database to the Dataherald service"""
        return self._api.connect_database(database_connection_request)

    def add_golden_records(self, golden_records: List) -> bool:
        """Takes in an English question and answers it based on content from the registered databases"""
        return self._api.add_golden_records(golden_records)

    def add_data_definition(
        self, data_definition_request: DataDefinitionRequest
    ) -> bool:
        """Takes in an English question and answers it based on content from the registered databases"""
        return self._api.add_data_definition(data_definition_request)

    def execute_query(self, query: Query) -> tuple[str, dict]:
        """Executes a query on the given db_alias"""
        return self._api.execute_query(query)

    def update_query(self, query_id: str, query: UpdateQueryRequest) -> NLQueryResponse:
        """Executes a query on the given db_alias"""
        return self._api.update_query(query_id, query)

    def execute_temp_query(
        self, query_id: str, query: ExecuteTempQueryRequest
    ) -> NLQueryResponse:
        """Executes a query on the given db_alias"""
        return self._api.execute_temp_query(query_id, query)
