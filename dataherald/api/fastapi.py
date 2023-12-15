import json
import logging
import os
import threading
import time
from typing import List

import openai
from bson import json_util
from bson.objectid import InvalidId, ObjectId
from fastapi import BackgroundTasks, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse, JSONResponse
from overrides import override

from dataherald.api import API
from dataherald.api.types import Query
from dataherald.config import Settings, System
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
from dataherald.eval import Evaluator
from dataherald.finetuning.openai_finetuning import OpenAIFineTuning
from dataherald.repositories.base import ResponseRepository
from dataherald.repositories.database_connections import DatabaseConnectionRepository
from dataherald.repositories.finetunings import FinetuningsRepository
from dataherald.repositories.golden_records import GoldenRecordRepository
from dataherald.repositories.instructions import InstructionRepository
from dataherald.repositories.question import QuestionRepository
from dataherald.sql_database.base import (
    InvalidDBConnectionError,
    SQLDatabase,
    SQLInjectionError,
)
from dataherald.sql_database.models.types import DatabaseConnection
from dataherald.sql_generator import SQLGenerator
from dataherald.sql_generator.generates_nl_answer import GeneratesNlAnswer
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
from dataherald.utils.models_context_window import OPENAI_CONTEXT_WIDNOW_SIZES
from dataherald.utils.s3 import S3

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
    def answer_question(
        self,
        run_evaluator: bool = True,
        generate_csv: bool = False,
        question_request: QuestionRequest = None,
        user_question: Question | None = None,
    ) -> Response:
        """Takes in an English question and answers it based on content from the registered databases"""
        sql_generation = self.system.instance(SQLGenerator)
        context_store = self.system.instance(ContextStore)

        if not user_question:
            user_question = Question(
                question=question_request.question,
                db_connection_id=question_request.db_connection_id,
            )
            question_repository = QuestionRepository(self.storage)
            user_question = question_repository.insert(user_question)
        logger.info(f"Answer question: {user_question.question}")

        db_connection_repository = DatabaseConnectionRepository(self.storage)
        database_connection = db_connection_repository.find_by_id(
            user_question.db_connection_id
        )
        response_repository = ResponseRepository(self.storage)

        if not database_connection:
            response = response_repository.insert(
                Response(
                    question_id=user_question.id,
                    error_message="Connections doesn't exist",
                    sql_query="",
                )
            )
            return JSONResponse(status_code=404, content=jsonable_encoder(response))
        try:
            context = context_store.retrieve_context_for_question(user_question)
            start_generated_answer = time.time()
            generated_answer = sql_generation.generate_response(
                user_question,
                database_connection,
                context[0],
                generate_csv,
            )
            logger.info("Starts evaluator...")
            if run_evaluator:
                evaluator = self.system.instance(Evaluator)
                confidence_score = evaluator.get_confidence_score(
                    user_question, generated_answer, database_connection
                )
                generated_answer.confidence_score = confidence_score
        except Exception as e:
            response = response_repository.insert(
                Response(
                    question_id=user_question.id, error_message=str(e), sql_query=""
                )
            )
            return JSONResponse(
                status_code=400,
                content=jsonable_encoder(response),
            )

        if (
            generate_csv
            and len(generated_answer.sql_query_result.rows)
            > MAX_ROWS_TO_CREATE_CSV_FILE
        ):
            generated_answer.sql_query_result = None
        generated_answer.exec_time = time.time() - start_generated_answer
        response_repository = ResponseRepository(self.storage)
        return response_repository.insert(generated_answer)

    @override
    def answer_question_with_timeout(
        self,
        run_evaluator: bool = True,
        generate_csv: bool = False,
        question_request: QuestionRequest = None,
    ) -> Response:
        result = None
        exception = None
        user_question = Question(
            question=question_request.question,
            db_connection_id=question_request.db_connection_id,
        )
        question_repository = QuestionRepository(self.storage)
        user_question = question_repository.insert(user_question)
        stop_event = threading.Event()

        def run_and_catch_exceptions():
            nonlocal result, exception
            if not stop_event.is_set():
                result = self.answer_question(
                    run_evaluator, generate_csv, None, user_question
                )

        thread = threading.Thread(target=run_and_catch_exceptions)
        thread.start()
        thread.join(timeout=int(os.getenv("DH_ENGINE_TIMEOUT")))
        if thread.is_alive():
            stop_event.set()
            response_repository = ResponseRepository(self.storage)
            response = response_repository.insert(
                Response(
                    question_id=user_question.id,
                    error_message="Timeout Error",
                    sql_query="",
                )
            )
            return JSONResponse(status_code=400, content=jsonable_encoder(response))
        return result

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
    def get_query_history(self, db_connection_id: str) -> list[QueryHistory]:
        query_history_repository = QueryHistoryRepository(self.storage)
        return query_history_repository.find_by(
            {"db_connection_id": ObjectId(db_connection_id)}
        )

    @override
    def get_responses(self, question_id: str | None = None) -> list[Response]:
        response_repository = ResponseRepository(self.storage)
        query = {}
        if question_id:
            query = {"question_id": ObjectId(question_id)}
        return response_repository.find_by(query)

    @override
    def get_response(self, response_id: str) -> Response:
        response_repository = ResponseRepository(self.storage)

        try:
            result = response_repository.find_by_id(response_id)
        except InvalidId as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

        if not result:
            raise HTTPException(status_code=404, detail="Question not found")

        return result

    @override
    def get_response_file(
        self, response_id: str, background_tasks: BackgroundTasks
    ) -> FileResponse:
        response_repository = ResponseRepository(self.storage)
        question_repository = QuestionRepository(self.storage)
        db_connection_repository = DatabaseConnectionRepository(self.storage)
        try:
            result = response_repository.find_by_id(response_id)
            question = question_repository.find_by_id(result.question_id)
            db_connection = db_connection_repository.find_by_id(
                question.db_connection_id
            )
        except InvalidId as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

        if not result:
            raise HTTPException(
                status_code=404, detail="Question, response, or db_connection not found"
            )

        # Check if the file is to be returned from server (locally) or from S3
        if Settings().only_store_csv_files_locally:
            file_location = result.csv_file_path
            # check if the file exists
            if not os.path.exists(file_location):
                raise HTTPException(
                    status_code=404,
                    detail="CSV file not found. Possibly deleted/removed from server.",
                )
        else:
            s3 = S3()

            file_location = s3.download(
                result.csv_file_path, db_connection.file_storage
            )
            background_tasks.add_task(delete_file, file_location)

        return FileResponse(
            file_location,
            media_type="text/csv",
        )

    @override
    def update_response(self, response_id: str) -> Response:
        response_repository = ResponseRepository(self.storage)

        try:
            response = response_repository.find_by_id(response_id)
        except InvalidId as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        if not response:
            raise HTTPException(status_code=404, detail="Question not found")

        start_generated_answer = time.time()
        try:
            generates_nl_answer = GeneratesNlAnswer(self.system, self.storage)
            response = generates_nl_answer.execute(response)
            response.exec_time = time.time() - start_generated_answer
            response_repository.update(response)
        except openai.AuthenticationError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e
        except SQLInjectionError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e
        return response

    @override
    def get_questions(self, db_connection_id: str | None = None) -> list[Question]:
        question_repository = QuestionRepository(self.storage)
        query = {}
        if db_connection_id:
            query = {"db_connection_id": ObjectId(db_connection_id)}

        return question_repository.find_by(query)

    @override
    def get_question(self, question_id: str) -> Question:
        question_repository = QuestionRepository(self.storage)

        try:
            result = question_repository.find_by_id(question_id)
        except InvalidId as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

        if not result:
            raise HTTPException(status_code=404, detail="Question not found")

        return result

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
    def create_response(
        self,
        run_evaluator: bool = True,
        sql_response_only: bool = False,
        generate_csv: bool = False,
        query_request: CreateResponseRequest = None,  # noqa: ARG002
    ) -> Response:
        question_repository = QuestionRepository(self.storage)
        response_repository = ResponseRepository(self.storage)
        user_question = question_repository.find_by_id(query_request.question_id)
        if not user_question:
            raise HTTPException(status_code=404, detail="Question not found")

        db_connection_repository = DatabaseConnectionRepository(self.storage)
        database_connection = db_connection_repository.find_by_id(
            user_question.db_connection_id
        )
        if not database_connection:
            raise HTTPException(status_code=404, detail="Database connection not found")

        try:
            if not query_request.sql_query:
                sql_generation = self.system.instance(SQLGenerator)
                context_store = self.system.instance(ContextStore)
                context = context_store.retrieve_context_for_question(user_question)
                start_generated_answer = time.time()
                response = sql_generation.generate_response(
                    user_question,
                    database_connection,
                    context[0],
                    generate_csv,
                )
            else:
                response = Response(
                    question_id=query_request.question_id,
                    sql_query=query_request.sql_query,
                )
                start_generated_answer = time.time()

                generates_nl_answer = GeneratesNlAnswer(self.system, self.storage)
                response = generates_nl_answer.execute(
                    response, sql_response_only, generate_csv
                )
        except openai.AuthenticationError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e
        except SQLInjectionError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e

        if run_evaluator:
            evaluator = self.system.instance(Evaluator)
            confidence_score = evaluator.get_confidence_score(
                user_question, response, database_connection
            )
            response.confidence_score = confidence_score
        if (
            generate_csv
            and len(response.sql_query_result.rows) > MAX_ROWS_TO_CREATE_CSV_FILE
        ):
            response.sql_query_result = None
        response.exec_time = time.time() - start_generated_answer
        response_repository.insert(response)
        return response

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
