import datetime
import io
import logging
import os
import time
from typing import List

from bson.objectid import InvalidId, ObjectId
from fastapi import BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
from overrides import override
from sqlalchemy.exc import SQLAlchemyError

from dataherald.api import API
from dataherald.api.types.requests import (
    NLGenerationRequest,
    NLGenerationsSQLGenerationRequest,
    PromptRequest,
    PromptSQLGenerationNLGenerationRequest,
    PromptSQLGenerationRequest,
    SQLGenerationRequest,
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
from dataherald.config import System
from dataherald.context_store import ContextStore
from dataherald.context_store.default import MalformedGoldenSQLError
from dataherald.db import DB
from dataherald.db_scanner import Scanner
from dataherald.db_scanner.models.types import (
    QueryHistory,
    TableDescription,
    TableDescriptionStatus,
)
from dataherald.db_scanner.repository.base import (
    InvalidColumnNameError,
    TableDescriptionRepository,
)
from dataherald.db_scanner.repository.query_history import QueryHistoryRepository
from dataherald.finetuning.openai_finetuning import OpenAIFineTuning
from dataherald.repositories.database_connections import (
    DatabaseConnectionNotFoundError,
    DatabaseConnectionRepository,
)
from dataherald.repositories.finetunings import FinetuningsRepository
from dataherald.repositories.golden_sqls import GoldenSQLRepository
from dataherald.repositories.instructions import InstructionRepository
from dataherald.repositories.nl_generations import NLGenerationNotFoundError
from dataherald.repositories.prompts import PromptNotFoundError
from dataherald.repositories.sql_generations import SQLGenerationNotFoundError
from dataherald.services.nl_generations import NLGenerationError, NLGenerationService
from dataherald.services.prompts import PromptService
from dataherald.services.sql_generations import (
    EmptySQLGenerationError,
    SQLGenerationError,
    SQLGenerationService,
)
from dataherald.sql_database.base import (
    InvalidDBConnectionError,
    SQLDatabase,
    SQLInjectionError,
)
from dataherald.sql_database.models.types import DatabaseConnection
from dataherald.types import (
    BaseLLM,
    CancelFineTuningRequest,
    DatabaseConnectionRequest,
    Finetuning,
    FineTuningRequest,
    FineTuningStatus,
    GoldenSQL,
    GoldenSQLRequest,
    Instruction,
    InstructionRequest,
    ScannerRequest,
    TableDescriptionRequest,
    UpdateInstruction,
)
from dataherald.utils.models_context_window import OPENAI_CONTEXT_WIDNOW_SIZES

logger = logging.getLogger(__name__)

MAX_ROWS_TO_CREATE_CSV_FILE = 50


def async_scanning(scanner, database, scanner_request, storage):
    scanner.scan(
        database,
        scanner_request.db_connection_id,
        scanner_request.table_names,
        TableDescriptionRepository(storage),
        QueryHistoryRepository(storage),
    )


def async_fine_tuning(storage, model):
    openai_fine_tuning = OpenAIFineTuning(storage, model)
    openai_fine_tuning.create_fintuning_dataset()
    openai_fine_tuning.create_fine_tuning_job()


def delete_file(file_location: str):
    os.remove(file_location)


class FastAPI(API):
    def __init__(self, system: System):
        super().__init__(system)
        self.system = system
        self.storage = self.system.instance(DB)

    @override
    def heartbeat(self) -> int:
        """Returns the current server time in nanoseconds to check if the server is alive"""
        return int(time.time_ns())

    @override
    def scan_db(
        self, scanner_request: ScannerRequest, background_tasks: BackgroundTasks
    ) -> list[TableDescriptionResponse]:
        """Takes a db_connection_id and scan all the tables columns"""
        db_connection_repository = DatabaseConnectionRepository(self.storage)

        db_connection = db_connection_repository.find_by_id(
            scanner_request.db_connection_id
        )
        if not db_connection:
            raise HTTPException(status_code=404, detail="Database connection not found")

        try:
            database = SQLDatabase.get_sql_engine(db_connection)
        except Exception as e:
            raise HTTPException(  # noqa: B904
                status_code=400,
                detail=f"Unable to connect to db: {scanner_request.db_connection_id}, {e}",
            )

        scanner = self.system.instance(Scanner)
        all_tables = scanner.get_all_tables_and_views(database)
        if scanner_request.table_names:
            for table in scanner_request.table_names:
                if table not in all_tables:
                    raise HTTPException(
                        status_code=404, detail=f"Table named: {table} doesn't exist"
                    )  # noqa: B904
        else:
            scanner_request.table_names = all_tables

        rows = scanner.synchronizing(
            scanner_request,
            TableDescriptionRepository(self.storage),
        )

        background_tasks.add_task(
            async_scanning, scanner, database, scanner_request, self.storage
        )
        return [TableDescriptionResponse(**row.dict()) for row in rows]

    @override
    def create_database_connection(
        self, database_connection_request: DatabaseConnectionRequest
    ) -> DatabaseConnectionResponse:
        try:
            db_connection = DatabaseConnection(
                alias=database_connection_request.alias,
                connection_uri=database_connection_request.connection_uri,
                path_to_credentials_file=database_connection_request.path_to_credentials_file,
                llm_api_key=database_connection_request.llm_api_key,
                use_ssh=database_connection_request.use_ssh,
                ssh_settings=database_connection_request.ssh_settings,
                file_storage=database_connection_request.file_storage,
                metadata=database_connection_request.metadata,
            )

            SQLDatabase.get_sql_engine(db_connection, True)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))  # noqa: B904
        except InvalidDBConnectionError as e:
            raise HTTPException(  # noqa: B904
                status_code=400,
                detail=f"{e}",
            )

        db_connection_repository = DatabaseConnectionRepository(self.storage)
        db_connection = db_connection_repository.insert(db_connection)
        return DatabaseConnectionResponse(**db_connection.dict())

    @override
    def list_database_connections(self) -> list[DatabaseConnectionResponse]:
        db_connection_repository = DatabaseConnectionRepository(self.storage)
        db_connections = db_connection_repository.find_all()
        return [
            DatabaseConnectionResponse(**db_connection.dict())
            for db_connection in db_connections
        ]

    @override
    def update_database_connection(
        self,
        db_connection_id: str,
        database_connection_request: DatabaseConnectionRequest,
    ) -> DatabaseConnectionResponse:
        try:
            db_connection = DatabaseConnection(
                id=db_connection_id,
                alias=database_connection_request.alias,
                connection_uri=database_connection_request.connection_uri,
                path_to_credentials_file=database_connection_request.path_to_credentials_file,
                llm_api_key=database_connection_request.llm_api_key,
                use_ssh=database_connection_request.use_ssh,
                ssh_settings=database_connection_request.ssh_settings,
                file_storage=database_connection_request.file_storage,
                metadata=database_connection_request.metadata,
            )

            SQLDatabase.get_sql_engine(db_connection, True)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))  # noqa: B904
        except InvalidDBConnectionError as e:
            raise HTTPException(  # noqa: B904
                status_code=400,
                detail=f"{e}",
            )
        db_connection_repository = DatabaseConnectionRepository(self.storage)
        db_connection = db_connection_repository.update(db_connection)
        return DatabaseConnectionResponse(**db_connection.dict())

    @override
    def update_table_description(
        self,
        table_description_id: str,
        table_description_request: TableDescriptionRequest,
    ) -> TableDescriptionResponse:
        scanner_repository = TableDescriptionRepository(self.storage)
        try:
            table = scanner_repository.find_by_id(table_description_id)
        except InvalidId as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

        if not table:
            raise HTTPException(
                status_code=404, detail="Scanned database table not found"
            )

        try:
            table_description = scanner_repository.update_fields(
                table, table_description_request
            )
            return TableDescriptionResponse(**table_description.dict())
        except InvalidColumnNameError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

    @override
    def list_table_descriptions(
        self, db_connection_id: str, table_name: str | None = None
    ) -> list[TableDescriptionResponse]:
        scanner_repository = TableDescriptionRepository(self.storage)
        table_descriptions = scanner_repository.find_by(
            {"db_connection_id": str(db_connection_id), "table_name": table_name}
        )

        if db_connection_id:
            db_connection_repository = DatabaseConnectionRepository(self.storage)
            db_connection = db_connection_repository.find_by_id(db_connection_id)
            database = SQLDatabase.get_sql_engine(db_connection)

            scanner = self.system.instance(Scanner)
            all_tables = scanner.get_all_tables_and_views(database)
            if table_name:
                all_tables = [table for table in all_tables if table == table_name]

            for table_description in table_descriptions:
                if table_description.table_name not in all_tables:
                    table_description.status = TableDescriptionStatus.DEPRECATED.value
                else:
                    all_tables.remove(table_description.table_name)
            for table in all_tables:
                table_descriptions.append(
                    TableDescription(
                        table_name=table,
                        status=TableDescriptionStatus.NOT_SCANNED.value,
                        db_connection_id=db_connection_id,
                        columns=[],
                    )
                )

        return [
            TableDescriptionResponse(**table_description.dict())
            for table_description in table_descriptions
        ]

    @override
    def get_table_description(
        self, table_description_id: str
    ) -> TableDescriptionResponse:
        scanner_repository = TableDescriptionRepository(self.storage)

        try:
            result = scanner_repository.find_by_id(table_description_id)
        except InvalidId as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

        if not result:
            raise HTTPException(status_code=404, detail="Table description not found")
        return TableDescriptionResponse(**result.dict())

    @override
    def create_prompt(self, prompt_request: PromptRequest) -> PromptResponse:
        prompt_service = PromptService(self.storage)
        try:
            prompt = prompt_service.create(prompt_request)
        except InvalidId as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        except DatabaseConnectionNotFoundError:
            raise HTTPException(  # noqa: B904
                status_code=404, detail="Database connection not found"
            )
        return PromptResponse(**prompt.dict())

    @override
    def get_prompt(self, prompt_id) -> PromptResponse:
        prompt_service = PromptService(self.storage)
        try:
            prompts = prompt_service.get({"_id": ObjectId(prompt_id)})
        except InvalidId as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

        if len(prompts) == 0:
            raise HTTPException(  # noqa: B904
                status_code=404, detail=f"Prompt {prompt_id} not found"
            )
        return PromptResponse(**prompts[0].dict())

    @override
    def update_prompt(
        self, prompt_id: str, update_metadata_request: UpdateMetadataRequest
    ) -> PromptResponse:
        prompt_service = PromptService(self.storage)
        try:
            prompt = prompt_service.update_metadata(prompt_id, update_metadata_request)
        except PromptNotFoundError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        return PromptResponse(**prompt.dict())

    @override
    def get_prompts(self, db_connection_id: str | None = None) -> List[PromptResponse]:
        prompt_service = PromptService(self.storage)
        query = {}
        if db_connection_id:
            query["db_connection_id"] = db_connection_id
        prompts = prompt_service.get(query)
        result = []
        for prompt in prompts:
            result.append(PromptResponse(**prompt.dict()))
        return result

    @override
    def get_query_history(self, db_connection_id: str) -> list[QueryHistory]:
        query_history_repository = QueryHistoryRepository(self.storage)
        return query_history_repository.find_by(
            {"db_connection_id": str(db_connection_id)}
        )

    @override
    def add_golden_sqls(
        self, golden_sqls: List[GoldenSQLRequest]
    ) -> List[GoldenSQLResponse]:
        """Takes in a list of NL <> SQL pairs and stores them to be used in prompts to the LLM"""
        context_store = self.system.instance(ContextStore)
        try:
            golden_sqls = context_store.add_golden_sqls(golden_sqls)
        except MalformedGoldenSQLError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        return [GoldenSQLResponse(**golden_sql.dict()) for golden_sql in golden_sqls]

    @override
    def execute_sql_query(self, sql_generation_id: str, max_rows: int = 100) -> list:
        """Executes a SQL query against the database and returns the results"""
        sql_generation_service = SQLGenerationService(self.system, self.storage)
        try:
            results = sql_generation_service.execute(sql_generation_id, max_rows)
        except SQLGenerationNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e
        except SQLInjectionError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        except SQLAlchemyError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        return results[1].get("result", [])

    @override
    def export_csv_file(self, sql_generation_id: str) -> io.StringIO:
        """Exports a SQL query to a CSV file"""
        sql_generation_service = SQLGenerationService(self.system, self.storage)
        try:
            csv_dataframe = sql_generation_service.create_dataframe(sql_generation_id)
            csv_stream = io.StringIO()
            csv_dataframe.to_csv(csv_stream, index=False)
        except SQLGenerationNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e
        except SQLInjectionError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        except SQLAlchemyError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        except EmptySQLGenerationError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        return csv_stream

    @override
    def delete_golden_sql(self, golden_sql_id: str) -> dict:
        context_store = self.system.instance(ContextStore)
        status = context_store.remove_golden_sqls([golden_sql_id])
        return {"status": status}

    @override
    def get_golden_sqls(
        self, db_connection_id: str = None, page: int = 1, limit: int = 10
    ) -> List[GoldenSQL]:
        golden_sqls_repository = GoldenSQLRepository(self.storage)
        if db_connection_id:
            return golden_sqls_repository.find_by(
                {"db_connection_id": str(db_connection_id)},
                page=page,
                limit=limit,
            )
        return golden_sqls_repository.find_all(page=page, limit=limit)

    @override
    def update_golden_sql(
        self, golden_sql_id: str, update_metadata_request: UpdateMetadataRequest
    ) -> GoldenSQL:
        golden_sqls_repository = GoldenSQLRepository(self.storage)
        golden_sql = golden_sqls_repository.find_by_id(golden_sql_id)
        if not golden_sql:
            raise HTTPException(status_code=404, detail="Golden record not found")
        golden_sql.metadata = update_metadata_request.metadata
        golden_sqls_repository.update(golden_sql)
        return golden_sql

    @override
    def add_instruction(
        self, instruction_request: InstructionRequest
    ) -> InstructionResponse:
        instruction_repository = InstructionRepository(self.storage)
        instruction = Instruction(
            instruction=instruction_request.instruction,
            db_connection_id=instruction_request.db_connection_id,
            metadata=instruction_request.metadata,
        )
        instruction = instruction_repository.insert(instruction)
        return InstructionResponse(**instruction.dict())

    @override
    def get_instructions(
        self, db_connection_id: str = None, page: int = 1, limit: int = 10
    ) -> List[InstructionResponse]:
        instruction_repository = InstructionRepository(self.storage)
        if db_connection_id:
            instructions = instruction_repository.find_by(
                {"db_connection_id": str(db_connection_id)},
                page=page,
                limit=limit,
            )
        else:
            instructions = instruction_repository.find_all(page=page, limit=limit)
        result = []
        for instruction in instructions:
            result.append(InstructionResponse(**instruction.dict()))
        return result

    @override
    def delete_instruction(self, instruction_id: str) -> dict:
        instruction_repository = InstructionRepository(self.storage)
        deleted = instruction_repository.delete_by_id(instruction_id)
        if deleted == 0:
            raise HTTPException(status_code=404, detail="Instruction not found")
        return {"status": "success"}

    @override
    def update_instruction(
        self,
        instruction_id: str,
        instruction_request: UpdateInstruction,
    ) -> InstructionResponse:
        instruction_repository = InstructionRepository(self.storage)
        instruction = instruction_repository.find_by_id(instruction_id)
        if not instruction:
            raise HTTPException(status_code=404, detail="Instruction not found")
        updated_instruction = Instruction(
            id=instruction_id,
            instruction=instruction_request.instruction,
            db_connection_id=instruction.db_connection_id,
            metadata=instruction_request.metadata,
        )
        instruction_repository.update(updated_instruction)
        return InstructionResponse(**updated_instruction.dict())

    @override
    def create_finetuning_job(
        self, fine_tuning_request: FineTuningRequest, background_tasks: BackgroundTasks
    ) -> Finetuning:
        db_connection_repository = DatabaseConnectionRepository(self.storage)

        db_connection = db_connection_repository.find_by_id(
            fine_tuning_request.db_connection_id
        )
        if not db_connection:
            raise HTTPException(status_code=404, detail="Database connection not found")

        golden_sqls_repository = GoldenSQLRepository(self.storage)
        golden_sqls = []
        if fine_tuning_request.golden_sqls:
            for golden_sql_id in fine_tuning_request.golden_sqls:
                golden_sql = golden_sqls_repository.find_by_id(golden_sql_id)
                if not golden_sql:
                    raise HTTPException(
                        status_code=404, detail="Golden record not found"
                    )
                golden_sqls.append(golden_sql)
        else:
            golden_sqls = golden_sqls_repository.find_by(
                {"db_connection_id": str(fine_tuning_request.db_connection_id)},
                page=0,
                limit=0,
            )
            if not golden_sqls:
                raise HTTPException(status_code=404, detail="No golden sqls found")
        default_base_llm = BaseLLM(
            model_provider="openai",
            model_name="gpt-3.5-turbo-1106",
        )
        base_llm = (
            fine_tuning_request.base_llm
            if fine_tuning_request.base_llm
            else default_base_llm
        )
        if base_llm.model_name not in OPENAI_CONTEXT_WIDNOW_SIZES:
            raise HTTPException(
                status_code=400,
                detail=f"Model {fine_tuning_request.base_llm.model_name} not supported",
            )
        model_repository = FinetuningsRepository(self.storage)
        model = model_repository.insert(
            Finetuning(
                db_connection_id=fine_tuning_request.db_connection_id,
                alias=fine_tuning_request.alias
                if fine_tuning_request.alias
                else f"{db_connection.alias}_{datetime.datetime.now().strftime('%Y%m%d%H')}",
                base_llm=base_llm,
                golden_sqls=[str(golden_sql.id) for golden_sql in golden_sqls],
                metadata=fine_tuning_request.metadata,
            )
        )

        background_tasks.add_task(async_fine_tuning, self.storage, model)

        return model

    @override
    def cancel_finetuning_job(
        self, cancel_fine_tuning_request: CancelFineTuningRequest
    ) -> Finetuning:
        model_repository = FinetuningsRepository(self.storage)
        model = model_repository.find_by_id(cancel_fine_tuning_request.finetuning_id)
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")

        if model.status == FineTuningStatus.SUCCEEDED.value:
            raise HTTPException(
                status_code=400, detail="Model has already succeeded. Cannot cancel."
            )
        if model.status == FineTuningStatus.FAILED.value:
            raise HTTPException(
                status_code=400, detail="Model has already failed. Cannot cancel."
            )
        if model.status == FineTuningStatus.CANCELLED.value:
            raise HTTPException(
                status_code=400, detail="Model has already been cancelled."
            )

        openai_fine_tuning = OpenAIFineTuning(self.storage, model)

        return openai_fine_tuning.cancel_finetuning_job()

    @override
    def get_finetunings(self, db_connection_id: str | None = None) -> list[Finetuning]:
        model_repository = FinetuningsRepository(self.storage)
        query = {}
        if db_connection_id:
            query["db_connection_id"] = db_connection_id
        models = model_repository.find_by(query)
        result = []
        for model in models:
            openai_fine_tuning = OpenAIFineTuning(self.storage, model)
            result.append(
                Finetuning(**openai_fine_tuning.retrieve_finetuning_job().dict())
            )
        return result

    @override
    def delete_finetuning_job(self, finetuning_job_id: str) -> dict:
        model_repository = FinetuningsRepository(self.storage)
        deleted = model_repository.delete_by_id(finetuning_job_id)
        if deleted == 0:
            raise HTTPException(status_code=404, detail="Model not found")
        return {"status": "success"}

    @override
    def get_finetuning_job(self, finetuning_job_id: str) -> Finetuning:
        model_repository = FinetuningsRepository(self.storage)
        model = model_repository.find_by_id(finetuning_job_id)
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        openai_fine_tuning = OpenAIFineTuning(self.storage, model)
        return openai_fine_tuning.retrieve_finetuning_job()

    @override
    def update_finetuning_job(
        self, finetuning_job_id: str, update_metadata_request: UpdateMetadataRequest
    ) -> Finetuning:
        model_repository = FinetuningsRepository(self.storage)
        model = model_repository.find_by_id(finetuning_job_id)
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        model.metadata = update_metadata_request.metadata
        return model_repository.update(model)

    @override
    def create_sql_generation(
        self, prompt_id: str, sql_generation_request: SQLGenerationRequest
    ) -> SQLGenerationResponse:
        try:
            ObjectId(prompt_id)
        except InvalidId as e:
            raise HTTPException(status_code=400, detail="Invalid prompt id") from e
        sql_generation_service = SQLGenerationService(self.system, self.storage)
        try:
            sql_generation = sql_generation_service.create(
                prompt_id, sql_generation_request
            )
        except PromptNotFoundError as e:
            return JSONResponse(
                status_code=400,
                content={"message": str(e.args[0]), "sql_generation_id": e.args[1]},
            )
        except SQLGenerationError as e:
            return JSONResponse(
                status_code=400,
                content={"message": str(e.args[0]), "sql_generation_id": e.args[1]},
            )
        except SQLInjectionError as e:
            return JSONResponse(
                status_code=400,
                content={"message": str(e.args[0]), "sql_generation_id": e.args[1]},
            )
        return SQLGenerationResponse(**sql_generation.dict())

    @override
    def create_prompt_and_sql_generation(
        self, prompt_sql_generation_request: PromptSQLGenerationRequest
    ) -> SQLGenerationResponse:
        prompt_service = PromptService(self.storage)
        try:
            prompt = prompt_service.create(prompt_sql_generation_request.prompt)
        except InvalidId as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        except DatabaseConnectionNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e

        sql_generation_service = SQLGenerationService(self.system, self.storage)
        try:
            sql_generation = sql_generation_service.create(
                prompt.id, prompt_sql_generation_request
            )
        except PromptNotFoundError as e:
            return JSONResponse(
                status_code=400,
                content={
                    "message": str(e.args[0]),
                    "prompt_id": prompt.id,
                    "sql_generation_id": e.args[1],
                },
            )
        except SQLGenerationError as e:
            return JSONResponse(
                status_code=400,
                content={
                    "message": str(e.args[0]),
                    "prompt_id": prompt.id,
                    "sql_generation_id": e.args[1],
                },
            )
        except SQLInjectionError as e:
            return JSONResponse(
                status_code=400,
                content={
                    "message": str(e.args[0]),
                    "prompt_id": prompt.id,
                    "sql_generation_id": e.args[1],
                },
            )
        return SQLGenerationResponse(**sql_generation.dict())

    @override
    def get_sql_generations(
        self, prompt_id: str | None = None
    ) -> list[SQLGenerationResponse]:
        sql_generation_service = SQLGenerationService(self.system, self.storage)
        query = {}
        if prompt_id:
            query["prompt_id"] = prompt_id
        sql_generations = sql_generation_service.get(query)
        result = []
        for sql_generation in sql_generations:
            result.append(SQLGenerationResponse(**sql_generation.dict()))
        return result

    @override
    def get_sql_generation(self, sql_generation_id: str) -> SQLGenerationResponse:
        sql_generation_service = SQLGenerationService(self.system, self.storage)
        try:
            sql_generations = sql_generation_service.get(
                {"_id": ObjectId(sql_generation_id)}
            )
        except InvalidId as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

        if len(sql_generations) == 0:
            raise HTTPException(
                status_code=404, detail=f"SQL Generation {sql_generation_id} not found"
            )
        return SQLGenerationResponse(**sql_generations[0].dict())

    @override
    def update_sql_generation(
        self, sql_generation_id: str, update_metadata_request: UpdateMetadataRequest
    ) -> SQLGenerationResponse:
        sql_generation_service = SQLGenerationService(self.system, self.storage)
        try:
            sql_generation = sql_generation_service.update_metadata(
                sql_generation_id, update_metadata_request
            )
        except SQLGenerationNotFoundError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        return SQLGenerationResponse(**sql_generation.dict())

    @override
    def create_nl_generation(
        self, sql_generation_id: str, nl_generation_request: NLGenerationRequest
    ) -> NLGenerationResponse:
        try:
            ObjectId(sql_generation_id)
        except InvalidId as e:
            raise HTTPException(
                status_code=400, detail="Invalid SQL generation id"
            ) from e
        nl_generation_service = NLGenerationService(self.system, self.storage)
        try:
            nl_generation = nl_generation_service.create(
                sql_generation_id, nl_generation_request
            )
        except SQLGenerationNotFoundError as e:
            return JSONResponse(
                status_code=400,
                content={"message": str(e.args[0]), "nl_generation_id": e.args[1]},
            )
        except NLGenerationError as e:
            return JSONResponse(
                status_code=400,
                content={"message": str(e.args[0]), "nl_generation_id": e.args[1]},
            )
        return NLGenerationResponse(**nl_generation.dict())

    @override
    def create_sql_and_nl_generation(
        self,
        prompt_id: str,
        nl_generation_sql_generation_request: NLGenerationsSQLGenerationRequest,
    ) -> NLGenerationResponse:
        try:
            ObjectId(prompt_id)
        except InvalidId as e:
            raise HTTPException(status_code=400, detail="Invalid prompt id") from e
        sql_generation_service = SQLGenerationService(self.system, self.storage)
        try:
            sql_generation = sql_generation_service.create(
                prompt_id, nl_generation_sql_generation_request.sql_generation
            )
        except PromptNotFoundError as e:
            return JSONResponse(
                status_code=400,
                content={
                    "message": str(e.args[0]),
                    "sql_generation_id": e.args[1],
                    "nl_generation_id": None,
                },
            )
        except SQLGenerationError as e:
            return JSONResponse(
                status_code=400,
                content={
                    "message": str(e.args[0]),
                    "sql_generation_id": e.args[1],
                    "nl_generation_id": None,
                },
            )
        except SQLInjectionError as e:
            return JSONResponse(
                status_code=400,
                content={
                    "message": str(e.args[0]),
                    "sql_generation_id": e.args[1],
                    "nl_generation_id": None,
                },
            )

        nl_generation_service = NLGenerationService(self.system, self.storage)
        try:
            nl_generation = nl_generation_service.create(
                sql_generation.id, nl_generation_sql_generation_request
            )
        except SQLGenerationNotFoundError as e:
            return JSONResponse(
                status_code=400,
                content={
                    "message": str(e.args[0]),
                    "sql_generation_id": sql_generation.id,
                    "nl_generation_id": e.args[1],
                },
            )
        except NLGenerationError as e:
            return JSONResponse(
                status_code=400,
                content={
                    "message": str(e.args[0]),
                    "sql_generation_id": sql_generation.id,
                    "nl_generation_id": e.args[1],
                },
            )
        nl_generation_dict = nl_generation.dict()
        return NLGenerationResponse(**nl_generation_dict)

    @override
    def create_prompt_sql_and_nl_generation(
        self, request: PromptSQLGenerationNLGenerationRequest
    ) -> NLGenerationResponse:
        prompt_service = PromptService(self.storage)
        try:
            prompt = prompt_service.create(request.sql_generation.prompt)
        except DatabaseConnectionNotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e  # noqa: B904

        sql_generation_service = SQLGenerationService(self.system, self.storage)
        try:
            sql_generation = sql_generation_service.create(
                prompt.id, request.sql_generation
            )
        except PromptNotFoundError as e:
            return JSONResponse(
                status_code=400,
                content={
                    "message": str(e.args[0]),
                    "prompt_id": prompt.id,
                    "sql_generation_id": e.args[1],
                    "nl_generation_id": None,
                },
            )
        except SQLGenerationError as e:
            return JSONResponse(
                status_code=400,
                content={
                    "message": str(e.args[0]),
                    "prompt_id": prompt.id,
                    "sql_generation_id": e.args[1],
                    "nl_generation_id": None,
                },
            )

        nl_generation_service = NLGenerationService(self.system, self.storage)
        try:
            nl_generation = nl_generation_service.create(sql_generation.id, request)
        except SQLGenerationNotFoundError as e:
            return JSONResponse(
                status_code=400,
                content={
                    "message": str(e.args[0]),
                    "prompt_id": prompt.id,
                    "sql_generation_id": sql_generation.id,
                    "nl_generation_id": e.args[1],
                },
            )
        except NLGenerationError as e:
            return JSONResponse(
                status_code=400,
                content={
                    "message": str(e.args[0]),
                    "prompt_id": prompt.id,
                    "sql_generation_id": sql_generation.id,
                    "nl_generation_id": e.args[1],
                },
            )
        return NLGenerationResponse(**nl_generation.dict())

    @override
    def get_nl_generations(
        self, sql_generation_id: str | None = None
    ) -> list[NLGenerationResponse]:
        nl_generation_service = NLGenerationService(self.system, self.storage)
        query = {}
        if sql_generation_id:
            query["sql_generation_id"] = sql_generation_id
        nl_generations = nl_generation_service.get(query)
        result = []
        for nl_generation in nl_generations:
            result.append(NLGenerationResponse(**nl_generation.dict()))
        return result

    @override
    def update_nl_generation(
        self, nl_generation_id: str, update_metadata_request: UpdateMetadataRequest
    ) -> NLGenerationResponse:
        nl_generation_service = NLGenerationService(self.system, self.storage)
        try:
            nl_generation = nl_generation_service.update_metadata(
                nl_generation_id, update_metadata_request
            )
        except NLGenerationNotFoundError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        return NLGenerationResponse(**nl_generation.dict())

    @override
    def get_nl_generation(self, nl_generation_id: str) -> NLGenerationResponse:
        nl_generation_service = NLGenerationService(self.system, self.storage)
        try:
            nl_generations = nl_generation_service.get(
                {"_id": ObjectId(nl_generation_id)}
            )
        except InvalidId as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

        if len(nl_generations) == 0:
            raise HTTPException(
                status_code=404,
                detail=f"NL Generation {nl_generation_id} not found",
            )
        return NLGenerationResponse(**nl_generations[0].dict())
