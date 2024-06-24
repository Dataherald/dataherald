import os
from typing import List

import fastapi
from fastapi import BackgroundTasks, status
from fastapi import FastAPI as _FastAPI
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.routing import APIRoute

import dataherald
from dataherald.api.types.query import Query
from dataherald.api.types.requests import (
    NLGenerationRequest,
    NLGenerationsSQLGenerationRequest,
    PromptRequest,
    PromptSQLGenerationNLGenerationRequest,
    PromptSQLGenerationRequest,
    SQLGenerationRequest,
    StreamPromptSQLGenerationRequest,
    UpdateMetadataRequest,
)
from dataherald.api.types.responses import (
    DatabaseConnectionResponse,
    GoldenSQLResponse,
    InstructionResponse,
    NLGenerationResponse,
    PromptResponse,
    SQLGenerationResponse,
    TableDescriptionResponse,
)
from dataherald.config import Settings
from dataherald.db_scanner.models.types import QueryHistory
from dataherald.sql_database.models.types import DatabaseConnection
from dataherald.types import (
    CancelFineTuningRequest,
    DatabaseConnectionRequest,
    Finetuning,
    FineTuningRequest,
    GoldenSQL,
    GoldenSQLRequest,
    InstructionRequest,
    RefreshTableDescriptionRequest,
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
            status_code=201,
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
            status_code=201,
            tags=["Table descriptions"],
        )

        self.router.add_api_route(
            "/api/v1/table-descriptions/refresh",
            self.refresh_table_description,
            methods=["POST"],
            status_code=201,
            tags=["Table descriptions"],
        )

        self.router.add_api_route(
            "/api/v1/table-descriptions/{table_description_id}",
            self.update_table_description,
            methods=["PUT"],
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
            "/api/v1/query-history",
            self.get_query_history,
            methods=["GET"],
            tags=["Query history"],
        )

        self.router.add_api_route(
            "/api/v1/golden-sqls/{golden_sql_id}",
            self.delete_golden_sql,
            methods=["DELETE"],
            tags=["Golden SQLs"],
        )

        self.router.add_api_route(
            "/api/v1/golden-sqls",
            self.add_golden_sqls,
            methods=["POST"],
            status_code=201,
            tags=["Golden SQLs"],
        )

        self.router.add_api_route(
            "/api/v1/golden-sqls",
            self.get_golden_sqls,
            methods=["GET"],
            tags=["Golden SQLs"],
        )

        self.router.add_api_route(
            "/api/v1/golden-sqls/{golden_sql_id}",
            self.update_golden_sql,
            methods=["PUT"],
            tags=["Golden SQLs"],
        )

        self.router.add_api_route(
            "/api/v1/prompts",
            self.create_prompt,
            methods=["POST"],
            status_code=201,
            tags=["Prompts"],
        )

        self.router.add_api_route(
            "/api/v1/prompts/{prompt_id}",
            self.get_prompt,
            methods=["GET"],
            tags=["Prompts"],
        )

        self.router.add_api_route(
            "/api/v1/prompts",
            self.get_prompts,
            methods=["GET"],
            tags=["Prompts"],
        )

        self.router.add_api_route(
            "/api/v1/prompts/{prompt_id}",
            self.update_prompt,
            methods=["PUT"],
            tags=["Prompts"],
        )

        self.router.add_api_route(
            "/api/v1/prompts/{prompt_id}/sql-generations",
            self.create_sql_generation,
            methods=["POST"],
            status_code=201,
            tags=["SQL Generation"],
        )

        self.router.add_api_route(
            "/api/v1/prompts/sql-generations",
            self.create_prompt_and_sql_generation,
            methods=["POST"],
            status_code=201,
            tags=["SQL Generation"],
        )

        self.router.add_api_route(
            "/api/v1/sql-generations",
            self.get_sql_generations,
            methods=["GET"],
            tags=["SQL Generation"],
        )

        self.router.add_api_route(
            "/api/v1/sql-generations/{sql_generation_id}",
            self.get_sql_generation,
            methods=["GET"],
            tags=["SQL Generation"],
        )

        self.router.add_api_route(
            "/api/v1/sql-generations/{sql_generation_id}",
            self.update_sql_generation,
            methods=["PUT"],
            tags=["SQL Generation"],
        )

        self.router.add_api_route(
            "/api/v1/sql-generations/{sql_generation_id}/execute",
            self.execute_sql_query,
            methods=["GET"],
            tags=["SQL Generation"],
        )

        self.router.add_api_route(
            "/api/v1/sql-generations/{sql_generation_id}/csv-file",
            self.export_csv_file,
            methods=["GET"],
            tags=["SQL Generation"],
        )

        self.router.add_api_route(
            "/api/v1/sql-generations/{sql_generation_id}/nl-generations",
            self.create_nl_generation,
            methods=["POST"],
            status_code=201,
            tags=["NL Generation"],
        )

        self.router.add_api_route(
            "/api/v1/prompts/{prompt_id}/sql-generations/nl-generations",
            self.create_sql_and_nl_generation,
            methods=["POST"],
            status_code=201,
            tags=["NL Generation"],
        )

        self.router.add_api_route(
            "/api/v1/prompts/sql-generations/nl-generations",
            self.create_prompt_sql_and_nl_generation,
            methods=["POST"],
            status_code=201,
            tags=["NL Generation"],
        )

        self.router.add_api_route(
            "/api/v1/nl-generations",
            self.get_nl_generations,
            methods=["GET"],
            tags=["NL Generation"],
        )

        self.router.add_api_route(
            "/api/v1/nl-generations/{nl_generation_id}",
            self.get_nl_generation,
            methods=["GET"],
            tags=["NL Generation"],
        )

        self.router.add_api_route(
            "/api/v1/nl-generations/{nl_generation_id}",
            self.update_nl_generation,
            methods=["PUT"],
            tags=["NL Generation"],
        )

        self.router.add_api_route(
            "/api/v1/instructions",
            self.add_instruction,
            methods=["POST"],
            status_code=201,
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
            "/api/v1/finetunings",
            self.create_finetuning_job,
            methods=["POST"],
            status_code=201,
            tags=["Finetunings"],
        )

        self.router.add_api_route(
            "/api/v1/finetunings",
            self.get_fintunings,
            methods=["GET"],
            tags=["Finetunings"],
        )

        self.router.add_api_route(
            "/api/v1/finetunings/{finetuning_id}",
            self.get_finetuning_job,
            methods=["GET"],
            tags=["Finetunings"],
        )

        self.router.add_api_route(
            "/api/v1/finetunings/{finetuning_id}",
            self.update_finetuning_job,
            methods=["PUT"],
            tags=["Finetunings"],
        )

        self.router.add_api_route(
            "/api/v1/finetunings/{finetuning_id}/cancel",
            self.cancel_finetuning_job,
            methods=["POST"],
            tags=["Finetunings"],
        )

        self.router.add_api_route(
            "/api/v1/finetunings/{finetuning_id}",
            self.delete_finetuning_job,
            methods=["DELETE"],
            tags=["Finetunings"],
        )

        self.router.add_api_route(
            "/api/v1/stream-sql-generation",
            self.stream_sql_generation,
            methods=["POST"],
            tags=["Stream SQL Generation"],
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
    ) -> list[TableDescriptionResponse]:
        return self._api.scan_db(scanner_request, background_tasks)

    def refresh_table_description(
        self, refresh_table_description: RefreshTableDescriptionRequest
    ) -> list[TableDescriptionResponse]:
        return self._api.refresh_table_description(refresh_table_description)

    def create_prompt(self, prompt_request: PromptRequest) -> PromptResponse:
        return self._api.create_prompt(prompt_request)

    def get_prompt(self, prompt_id: str) -> PromptResponse:
        return self._api.get_prompt(prompt_id)

    def update_prompt(
        self, prompt_id: str, update_metadata_request: UpdateMetadataRequest
    ) -> PromptResponse:
        return self._api.update_prompt(prompt_id, update_metadata_request)

    def get_prompts(self, db_connection_id: str | None = None) -> list[PromptResponse]:
        return self._api.get_prompts(db_connection_id)

    def create_sql_generation(
        self, prompt_id: str, sql_generation_request: SQLGenerationRequest
    ) -> SQLGenerationResponse:
        return self._api.create_sql_generation(prompt_id, sql_generation_request)

    def create_prompt_and_sql_generation(
        self, prompt_sql_generation_request: PromptSQLGenerationRequest
    ) -> SQLGenerationResponse:
        return self._api.create_prompt_and_sql_generation(prompt_sql_generation_request)

    def get_sql_generations(
        self, prompt_id: str | None = None
    ) -> list[SQLGenerationResponse]:
        return self._api.get_sql_generations(prompt_id)

    def get_sql_generation(self, sql_generation_id: str) -> SQLGenerationResponse:
        return self._api.get_sql_generation(sql_generation_id)

    def update_sql_generation(
        self, sql_generation_id: str, update_metadata_request: UpdateMetadataRequest
    ) -> SQLGenerationResponse:
        return self._api.update_sql_generation(
            sql_generation_id, update_metadata_request
        )

    def create_nl_generation(
        self, sql_generation_id: str, nl_generation_request: NLGenerationRequest
    ) -> NLGenerationResponse:
        return self._api.create_nl_generation(sql_generation_id, nl_generation_request)

    def create_sql_and_nl_generation(
        self,
        prompt_id: str,
        nl_generation_sql_generation_request: NLGenerationsSQLGenerationRequest,
    ) -> NLGenerationResponse:
        return self._api.create_sql_and_nl_generation(
            prompt_id, nl_generation_sql_generation_request
        )

    def create_prompt_sql_and_nl_generation(
        self, request: PromptSQLGenerationNLGenerationRequest
    ) -> NLGenerationResponse:
        return self._api.create_prompt_sql_and_nl_generation(request)

    def get_nl_generations(
        self, sql_generation_id: str | None = None
    ) -> list[NLGenerationResponse]:
        return self._api.get_nl_generations(sql_generation_id)

    def get_nl_generation(self, nl_generation_id: str) -> NLGenerationResponse:
        return self._api.get_nl_generation(nl_generation_id)

    def update_nl_generation(
        self, nl_generation_id: str, update_metadata_request: UpdateMetadataRequest
    ) -> NLGenerationResponse:
        return self._api.update_nl_generation(nl_generation_id, update_metadata_request)

    def root(self) -> dict[str, int]:
        return {"nanosecond heartbeat": self._api.heartbeat()}

    def heartbeat(self) -> dict[str, int]:
        return self.root()

    def create_database_connection(
        self, database_connection_request: DatabaseConnectionRequest
    ) -> DatabaseConnectionResponse:
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
    ) -> TableDescriptionResponse:
        """Add descriptions for tables and columns"""
        return self._api.update_table_description(
            table_description_id, table_description_request
        )

    def list_table_descriptions(
        self, db_connection_id: str, table_name: str | None = None
    ) -> list[TableDescriptionResponse]:
        """List table descriptions"""
        return self._api.list_table_descriptions(db_connection_id, table_name)

    def get_table_description(
        self, table_description_id: str
    ) -> TableDescriptionResponse:
        """Get description"""
        return self._api.get_table_description(table_description_id)

    def get_query_history(self, db_connection_id: str) -> list[QueryHistory]:
        """Get description"""
        return self._api.get_query_history(db_connection_id)

    def execute_sql_query(self, sql_generation_id: str, max_rows: int = 100) -> list:
        """Executes a query on the given db_connection_id"""
        return self._api.execute_sql_query(sql_generation_id, max_rows)

    def export_csv_file(self, sql_generation_id: str) -> StreamingResponse:
        """Exports a CSV file for the given sql_generation_id"""
        stream = self._api.export_csv_file(sql_generation_id)

        response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
        response.headers["Content-Disposition"] = (
            f"attachment; filename=sql_generation_{sql_generation_id}.csv"
        )
        return response

    def delete_golden_sql(self, golden_sql_id: str) -> dict:
        """Deletes a golden record"""
        return self._api.delete_golden_sql(golden_sql_id)

    def add_golden_sqls(
        self, golden_sqls: List[GoldenSQLRequest]
    ) -> List[GoldenSQLResponse]:
        return self._api.add_golden_sqls(golden_sqls)

    def get_golden_sqls(
        self, db_connection_id: str = None, page: int = 1, limit: int = 10
    ) -> List[GoldenSQL]:
        """Gets golden sqls"""
        return self._api.get_golden_sqls(db_connection_id, page, limit)

    def update_golden_sql(
        self, golden_sql_id: str, update_metadata_request: UpdateMetadataRequest
    ) -> GoldenSQL:
        """Gets golden sqls"""
        return self._api.update_golden_sql(golden_sql_id, update_metadata_request)

    def add_instruction(
        self, instruction_request: InstructionRequest
    ) -> InstructionResponse:
        """Adds an instruction"""
        created_records = self._api.add_instruction(instruction_request)

        # Return a JSONResponse with status code 201 and the location header.
        instruction_as_dict = created_records.dict()

        return JSONResponse(
            content=instruction_as_dict, status_code=status.HTTP_201_CREATED
        )

    def get_instructions(
        self, db_connection_id: str = None, page: int = 1, limit: int = 10
    ) -> List[InstructionResponse]:
        """Gets instructions"""
        return self._api.get_instructions(db_connection_id, page, limit)

    def delete_instruction(self, instruction_id: str) -> dict:
        """Deletes an instruction"""
        return self._api.delete_instruction(instruction_id)

    def update_instruction(
        self,
        instruction_id: str,
        instruction_request: UpdateInstruction,
    ) -> InstructionResponse:
        """Updates an instruction"""
        return self._api.update_instruction(instruction_id, instruction_request)

    def create_finetuning_job(
        self, fine_tuning_request: FineTuningRequest, background_tasks: BackgroundTasks
    ) -> Finetuning:
        """Creates a fine tuning job"""
        return self._api.create_finetuning_job(fine_tuning_request, background_tasks)

    def cancel_finetuning_job(
        self, cancel_fine_tuning_request: CancelFineTuningRequest
    ) -> Finetuning:
        """Cancels a fine tuning job"""
        return self._api.cancel_finetuning_job(cancel_fine_tuning_request)

    def get_finetuning_job(self, finetuning_id: str) -> Finetuning:
        """Gets fine tuning jobs"""
        return self._api.get_finetuning_job(finetuning_id)

    def get_fintunings(self, db_connection_id: str = None) -> list[Finetuning]:
        """Gets fine tuning jobs"""
        return self._api.get_finetunings(db_connection_id)

    def delete_finetuning_job(self, finetuning_id: str) -> dict:
        """Deletes a fine tuning job"""
        return self._api.delete_finetuning_job(finetuning_id)

    def update_finetuning_job(
        self, finetuning_id: str, update_metadata_request: UpdateMetadataRequest
    ) -> Finetuning:
        """Gets fine tuning jobs"""
        return self._api.update_finetuning_job(finetuning_id, update_metadata_request)

    async def stream_sql_generation(
        self, request: StreamPromptSQLGenerationRequest
    ) -> StreamingResponse:
        return StreamingResponse(
            self._api.stream_create_prompt_and_sql_generation(request),
            media_type="text/event-stream",
        )
