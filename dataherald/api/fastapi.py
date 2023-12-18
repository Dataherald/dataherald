import json
import logging
import os
import time
from typing import List

from bson import json_util
from bson.objectid import InvalidId, ObjectId
from fastapi import BackgroundTasks, HTTPException
from overrides import override

from dataherald.api import API
from dataherald.api.types.query import Query
from dataherald.api.types.requests import (
    NLGenerationRequest,
    PromptRequest,
    SQLGenerationRequest,
)
from dataherald.api.types.responses import (
    NLGenerationResponse,
    PromptResponse,
    SQLGenerationResponse,
)
from dataherald.config import System
from dataherald.context_store import ContextStore
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
from dataherald.repositories.golden_records import GoldenRecordRepository
from dataherald.repositories.instructions import InstructionRepository
from dataherald.repositories.prompts import PromptNotFoundError
from dataherald.repositories.sql_generations import SQLGenerationNotFoundError
from dataherald.services.nl_generations import NLGenerationError, NLGenerationService
from dataherald.services.prompts import PromptService
from dataherald.services.sql_generations import SQLGenerationError, SQLGenerationService
from dataherald.sql_database.base import (
    InvalidDBConnectionError,
    SQLDatabase,
    SQLInjectionError,
)
from dataherald.sql_database.models.types import DatabaseConnection
from dataherald.types import (
    CancelFineTuningRequest,
    DatabaseConnectionRequest,
    Finetuning,
    FineTuningRequest,
    GoldenRecord,
    GoldenRecordRequest,
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
    ) -> bool:
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

        scanner.synchronizing(
            scanner_request.table_names,
            scanner_request.db_connection_id,
            TableDescriptionRepository(self.storage),
        )

        background_tasks.add_task(
            async_scanning, scanner, database, scanner_request, self.storage
        )
        return True

    @override
    def create_database_connection(
        self, database_connection_request: DatabaseConnectionRequest
    ) -> DatabaseConnection:
        try:
            db_connection = DatabaseConnection(
                alias=database_connection_request.alias,
                uri=database_connection_request.connection_uri,
                path_to_credentials_file=database_connection_request.path_to_credentials_file,
                llm_api_key=database_connection_request.llm_api_key,
                use_ssh=database_connection_request.use_ssh,
                ssh_settings=database_connection_request.ssh_settings,
                file_storage=database_connection_request.file_storage,
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
        return db_connection_repository.insert(db_connection)

    @override
    def list_database_connections(self) -> list[DatabaseConnection]:
        db_connection_repository = DatabaseConnectionRepository(self.storage)
        return db_connection_repository.find_all()

    @override
    def update_database_connection(
        self,
        db_connection_id: str,
        database_connection_request: DatabaseConnectionRequest,
    ) -> DatabaseConnection:
        try:
            db_connection = DatabaseConnection(
                id=db_connection_id,
                alias=database_connection_request.alias,
                uri=database_connection_request.connection_uri,
                path_to_credentials_file=database_connection_request.path_to_credentials_file,
                llm_api_key=database_connection_request.llm_api_key,
                use_ssh=database_connection_request.use_ssh,
                ssh_settings=database_connection_request.ssh_settings,
                file_storage=database_connection_request.file_storage,
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
        return db_connection_repository.update(db_connection)

    @override
    def update_table_description(
        self,
        table_description_id: str,
        table_description_request: TableDescriptionRequest,
    ) -> TableDescription:
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
            return scanner_repository.update_fields(table, table_description_request)
        except InvalidColumnNameError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

    @override
    def list_table_descriptions(
        self, db_connection_id: str, table_name: str | None = None
    ) -> list[TableDescription]:
        scanner_repository = TableDescriptionRepository(self.storage)
        table_descriptions = scanner_repository.find_by(
            {"db_connection_id": ObjectId(db_connection_id), "table_name": table_name}
        )

        if db_connection_id:
            db_connection_repository = DatabaseConnectionRepository(self.storage)
            db_connection = db_connection_repository.find_by_id(db_connection_id)
            database = SQLDatabase.get_sql_engine(db_connection)

            scanner = self.system.instance(Scanner)
            all_tables = scanner.get_all_tables_and_views(database)

            for table_description in table_descriptions:
                if table_description.table_name not in all_tables:
                    table_description.status = TableDescriptionStatus.DEPRECATED.value
                else:
                    all_tables.remove(table_description.table_name)
            for table in all_tables:
                table_descriptions.append(
                    TableDescription(
                        table_name=table,
                        status=TableDescriptionStatus.NOT_SYNCHRONIZED.value,
                        db_connection_id=db_connection_id,
                        columns=[],
                    )
                )

        return table_descriptions

    @override
    def get_table_description(self, table_description_id: str) -> TableDescription:
        scanner_repository = TableDescriptionRepository(self.storage)

        try:
            result = scanner_repository.find_by_id(table_description_id)
        except InvalidId as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

        if not result:
            raise HTTPException(status_code=404, detail="Table description not found")
        return result

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
        prompt_dict = prompt.dict()
        prompt_dict["created_at"] = str(prompt.created_at)
        return PromptResponse(**prompt_dict)

    @override
    def get_query_history(self, db_connection_id: str) -> list[QueryHistory]:
        query_history_repository = QueryHistoryRepository(self.storage)
        return query_history_repository.find_by(
            {"db_connection_id": ObjectId(db_connection_id)}
        )

    @override
    def add_golden_records(
        self, golden_records: List[GoldenRecordRequest]
    ) -> List[GoldenRecord]:
        """Takes in a list of NL <> SQL pairs and stores them to be used in prompts to the LLM"""
        context_store = self.system.instance(ContextStore)
        return context_store.add_golden_records(golden_records)

    @override
    def execute_sql_query(self, query: Query) -> tuple[str, dict]:
        """Executes a SQL query against the database and returns the results"""
        db_connection_repository = DatabaseConnectionRepository(self.storage)
        database_connection = db_connection_repository.find_by_id(
            query.db_connection_id
        )
        if not database_connection:
            raise HTTPException(status_code=404, detail="Database connection not found")
        database = SQLDatabase.get_sql_engine(database_connection)
        try:
            result = database.run_sql(query.sql_query)
        except SQLInjectionError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e
        return result

    @override
    def delete_golden_record(self, golden_record_id: str) -> dict:
        context_store = self.system.instance(ContextStore)
        status = context_store.remove_golden_records([golden_record_id])
        return {"status": status}

    @override
    def get_golden_records(
        self, db_connection_id: str = None, page: int = 1, limit: int = 10
    ) -> List[GoldenRecord]:
        golden_records_repository = GoldenRecordRepository(self.storage)
        if db_connection_id:
            return golden_records_repository.find_by(
                {"db_connection_id": ObjectId(db_connection_id)},
                page=page,
                limit=limit,
            )
        return golden_records_repository.find_all(page=page, limit=limit)

    @override
    def add_instruction(self, instruction_request: InstructionRequest) -> Instruction:
        instruction_repository = InstructionRepository(self.storage)
        instruction = Instruction(
            instruction=instruction_request.instruction,
            db_connection_id=instruction_request.db_connection_id,
        )
        return instruction_repository.insert(instruction)

    @override
    def get_instructions(
        self, db_connection_id: str = None, page: int = 1, limit: int = 10
    ) -> List[Instruction]:
        instruction_repository = InstructionRepository(self.storage)
        if db_connection_id:
            return instruction_repository.find_by(
                {"db_connection_id": ObjectId(db_connection_id)},
                page=page,
                limit=limit,
            )
        return instruction_repository.find_all(page=page, limit=limit)

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
    ) -> Instruction:
        instruction_repository = InstructionRepository(self.storage)
        instruction = instruction_repository.find_by_id(instruction_id)
        if not instruction:
            raise HTTPException(status_code=404, detail="Instruction not found")
        updated_instruction = Instruction(
            id=instruction_id,
            instruction=instruction_request.instruction,
            db_connection_id=instruction.db_connection_id,
        )
        instruction_repository.update(updated_instruction)
        return json.loads(json_util.dumps(updated_instruction))

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

        golden_records_repository = GoldenRecordRepository(self.storage)
        golden_records = []
        if fine_tuning_request.golden_records:
            for golden_record_id in fine_tuning_request.golden_records:
                golden_record = golden_records_repository.find_by_id(golden_record_id)
                if not golden_record:
                    raise HTTPException(
                        status_code=404, detail="Golden record not found"
                    )
                golden_records.append(golden_record)
        else:
            golden_records = golden_records_repository.find_by(
                {"db_connection_id": ObjectId(fine_tuning_request.db_connection_id)},
                page=0,
                limit=0,
            )
            if not golden_records:
                raise HTTPException(status_code=404, detail="No golden records found")

        if fine_tuning_request.base_llm.model_name not in OPENAI_CONTEXT_WIDNOW_SIZES:
            raise HTTPException(
                status_code=400,
                detail=f"Model {fine_tuning_request.base_llm.model_name} not supported",
            )

        model_repository = FinetuningsRepository(self.storage)
        model = model_repository.insert(
            Finetuning(
                db_connection_id=fine_tuning_request.db_connection_id,
                alias=fine_tuning_request.alias,
                base_llm=fine_tuning_request.base_llm,
                golden_records=[
                    str(golden_record.id) for golden_record in golden_records
                ],
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

        if model.status == "succeeded":
            raise HTTPException(
                status_code=400, detail="Model has already succeeded. Cannot cancel."
            )
        if model.status == "failed":
            raise HTTPException(
                status_code=400, detail="Model has already failed. Cannot cancel."
            )
        if model.status == "cancelled":
            raise HTTPException(
                status_code=400, detail="Model has already been cancelled."
            )

        openai_fine_tuning = OpenAIFineTuning(self.storage, model)

        return openai_fine_tuning.cancel_finetuning_job()

    @override
    def get_finetuning_job(self, finetuning_job_id: str) -> Finetuning:
        model_repository = FinetuningsRepository(self.storage)
        model = model_repository.find_by_id(finetuning_job_id)
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        openai_fine_tuning = OpenAIFineTuning(self.storage, model)
        return openai_fine_tuning.retrieve_finetuning_job()

    @override
    def create_sql_generation(
        self, prompt_id: str, sql_generation_request: SQLGenerationRequest
    ) -> SQLGenerationResponse:
        sql_generation_service = SQLGenerationService(self.system, self.storage)
        try:
            sql_generation = sql_generation_service.create(
                prompt_id, sql_generation_request
            )
        except InvalidId as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        except PromptNotFoundError as e:
            raise HTTPException(status_code=404, detail="Prompt not found") from e
        except SQLGenerationError as e:
            raise HTTPException(
                status_code=400, detail="Error raised during SQL generation"
            ) from e
        sql_generation_dict = sql_generation.dict()
        sql_generation_dict["created_at"] = str(sql_generation.created_at)
        sql_generation_dict["completed_at"] = str(sql_generation.completed_at)
        return SQLGenerationResponse(**sql_generation_dict)

    @override
    def create_prompt_and_sql_generation(
        self, prompt: PromptRequest, sql_generation: SQLGenerationRequest
    ) -> SQLGenerationResponse:
        prompt_service = PromptService(self.storage)
        try:
            prompt = prompt_service.create(prompt)
        except InvalidId as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        except DatabaseConnectionNotFoundError:
            raise HTTPException(  # noqa: B904
                status_code=404, detail="Database connection not found"
            )

        sql_generation_service = SQLGenerationService(self.system, self.storage)
        try:
            sql_generation = sql_generation_service.create(prompt.id, sql_generation)
        except InvalidId as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        except PromptNotFoundError as e:
            raise HTTPException(status_code=404, detail="Prompt not found") from e
        except SQLGenerationError as e:
            raise HTTPException(
                status_code=400, detail="Error raised during SQL generation"
            ) from e
        sql_generation_dict = sql_generation.dict()
        sql_generation_dict["created_at"] = str(sql_generation.created_at)
        sql_generation_dict["completed_at"] = str(sql_generation.completed_at)
        return SQLGenerationResponse(**sql_generation_dict)

    @override
    def create_nl_generation(
        self, sql_generation_id: str, nl_generation_request: NLGenerationRequest
    ) -> NLGenerationResponse:
        nl_generation_service = NLGenerationService(self.system, self.storage)
        try:
            nl_generation = nl_generation_service.create(
                sql_generation_id, nl_generation_request
            )
        except InvalidId as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        except SQLGenerationNotFoundError as e:
            raise HTTPException(
                status_code=400, detail="SQL Generation not found"
            ) from e
        except NLGenerationError as e:
            raise HTTPException(
                status_code=400, detail="Error raised during NL generation"
            ) from e
        nl_generation_dict = nl_generation.dict()
        nl_generation_dict["created_at"] = str(nl_generation.created_at)
        return NLGenerationResponse(**nl_generation_dict)

    @override
    def create_sql_and_nl_generation(
        self,
        prompt_id: str,
        sql_generation: SQLGenerationRequest,
        nl_generation: NLGenerationRequest,
    ) -> NLGenerationResponse:
        sql_generation_service = SQLGenerationService(self.system, self.storage)
        try:
            sql_generation = sql_generation_service.create(prompt_id, sql_generation)
        except InvalidId as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        except PromptNotFoundError as e:
            raise HTTPException(status_code=404, detail="Prompt not found") from e
        except SQLGenerationError as e:
            raise HTTPException(
                status_code=400, detail="Error raised during SQL generation"
            ) from e

        nl_generation_service = NLGenerationService(self.system, self.storage)
        try:
            nl_generation = nl_generation_service.create(
                sql_generation.id, nl_generation
            )
        except InvalidId as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        except SQLGenerationNotFoundError as e:
            raise HTTPException(
                status_code=400, detail="SQL Generation not found"
            ) from e
        except NLGenerationError as e:
            raise HTTPException(
                status_code=400, detail="Error raised during NL generation"
            ) from e
        nl_generation_dict = nl_generation.dict()
        nl_generation_dict["created_at"] = str(nl_generation.created_at)
        return NLGenerationResponse(**nl_generation_dict)

    @override
    def create_prompt_sql_and_nl_generation(
        self,
        prompt: PromptRequest,
        sql_generation: SQLGenerationRequest,
        nl_generation: NLGenerationRequest,
    ) -> NLGenerationResponse:
        prompt_service = PromptService(self.storage)
        try:
            prompt = prompt_service.create(prompt)
        except InvalidId as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        except DatabaseConnectionNotFoundError:
            raise HTTPException(  # noqa: B904
                status_code=404, detail="Database connection not found"
            )

        sql_generation_service = SQLGenerationService(self.system, self.storage)
        try:
            sql_generation = sql_generation_service.create(prompt.id, sql_generation)
        except InvalidId as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        except PromptNotFoundError as e:
            raise HTTPException(status_code=404, detail="Prompt not found") from e
        except SQLGenerationError as e:
            raise HTTPException(
                status_code=400, detail="Error raised during SQL generation"
            ) from e

        nl_generation_service = NLGenerationService(self.system, self.storage)
        try:
            nl_generation = nl_generation_service.create(
                sql_generation.id, nl_generation
            )
        except InvalidId as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        except SQLGenerationNotFoundError as e:
            raise HTTPException(
                status_code=400, detail="SQL Generation not found"
            ) from e
        except NLGenerationError as e:
            raise HTTPException(
                status_code=400, detail="Error raised during NL generation"
            ) from e
        nl_generation_dict = nl_generation.dict()
        nl_generation_dict["created_at"] = str(nl_generation.created_at)
        return NLGenerationResponse(**nl_generation_dict)
