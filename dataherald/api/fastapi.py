import json
import logging
import time
from typing import List

from bson import json_util
from bson.objectid import ObjectId
from fastapi import BackgroundTasks, HTTPException
from overrides import override

from dataherald.api import API
from dataherald.api.types import Query
from dataherald.config import System
from dataherald.context_store import ContextStore
from dataherald.db import DB
from dataherald.db_scanner import Scanner
from dataherald.db_scanner.models.types import TableDescription, TableDescriptionStatus
from dataherald.db_scanner.repository.base import TableDescriptionRepository
from dataherald.eval import Evaluator
from dataherald.repositories.base import ResponseRepository
from dataherald.repositories.database_connections import DatabaseConnectionRepository
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

logger = logging.getLogger(__name__)


def async_scanning(scanner, database, scanner_request, storage):
    scanner.scan(
        database,
        scanner_request.db_connection_id,
        scanner_request.table_names,
        TableDescriptionRepository(storage),
    )


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
    def answer_question(self, question_request: QuestionRequest) -> Response:
        """Takes in an English question and answers it based on content from the registered databases"""
        logger.info(f"Answer question: {question_request.question}")
        sql_generation = self.system.instance(SQLGenerator)
        evaluator = self.system.instance(Evaluator)
        context_store = self.system.instance(ContextStore)

        user_question = Question(
            question=question_request.question,
            db_connection_id=question_request.db_connection_id,
        )

        question_repository = QuestionRepository(self.storage)
        user_question = question_repository.insert(user_question)

        db_connection_repository = DatabaseConnectionRepository(self.storage)
        database_connection = db_connection_repository.find_by_id(
            question_request.db_connection_id
        )
        if not database_connection:
            raise HTTPException(status_code=404, detail="Database connection not found")
        context = context_store.retrieve_context_for_question(user_question)
        start_generated_answer = time.time()
        try:
            generated_answer = sql_generation.generate_response(
                user_question, database_connection, context[0]
            )
            logger.info("Starts evaluator...")
            confidence_score = evaluator.get_confidence_score(
                user_question, generated_answer, database_connection
            )
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e
        except SQLInjectionError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e
        generated_answer.confidence_score = confidence_score
        generated_answer.exec_time = time.time() - start_generated_answer
        response_repository = ResponseRepository(self.storage)
        return response_repository.insert(generated_answer)

    @override
    def create_database_connection(
        self, database_connection_request: DatabaseConnectionRequest
    ) -> DatabaseConnection:
        try:
            db_connection = DatabaseConnection(
                alias=database_connection_request.alias,
                uri=database_connection_request.connection_uri,
                path_to_credentials_file=database_connection_request.path_to_credentials_file,
                llm_credentials=database_connection_request.llm_credentials,
                use_ssh=database_connection_request.use_ssh,
                ssh_settings=database_connection_request.ssh_settings,
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
                llm_credentials=database_connection_request.llm_credentials,
                use_ssh=database_connection_request.use_ssh,
                ssh_settings=database_connection_request.ssh_settings,
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
        table = scanner_repository.find_by_id(table_description_id)

        if not table:
            raise HTTPException(
                status_code=404, detail="Scanned database table not found"
            )

        if table_description_request.description:
            table.description = table_description_request.description
        if table_description_request.columns:
            for column_request in table_description_request.columns:
                for column in table.columns:
                    if column_request.name == column.name:
                        column.description = column_request.description

        return scanner_repository.update(table)

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
        return scanner_repository.find_by_id(table_description_id)

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
        return response_repository.find_by_id(response_id)

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
        return question_repository.find_by_id(question_id)

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
        self, query_request: CreateResponseRequest  # noqa: ARG002
    ) -> Response:
        evaluator = self.system.instance(Evaluator)
        question_repository = QuestionRepository(self.storage)
        user_question = question_repository.find_by_id(query_request.question_id)
        db_connection_repository = DatabaseConnectionRepository(self.storage)
        database_connection = db_connection_repository.find_by_id(
            user_question.db_connection_id
        )
        if not database_connection:
            raise HTTPException(status_code=404, detail="Database connection not found")

        response = Response(
            question_id=query_request.question_id, sql_query=query_request.sql_query
        )
        response_repository = ResponseRepository(self.storage)
        response_repository.insert(response)
        start_generated_answer = time.time()
        try:
            generates_nl_answer = GeneratesNlAnswer(self.system, self.storage)
            response = generates_nl_answer.execute(response)
            confidence_score = evaluator.get_confidence_score(
                user_question, response, database_connection
            )
            response.confidence_score = confidence_score
            response.exec_time = time.time() - start_generated_answer
            response_repository.update(response)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e
        except SQLInjectionError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e
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
