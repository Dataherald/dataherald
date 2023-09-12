import json
import logging
import time
from typing import List

from bson import json_util
from fastapi import HTTPException
from overrides import override

from dataherald.api import API
from dataherald.api.types import Query
from dataherald.config import System
from dataherald.context_store import ContextStore
from dataherald.db import DB
from dataherald.db_scanner import Scanner
from dataherald.db_scanner.models.types import TableSchemaDetail
from dataherald.db_scanner.repository.base import DBScannerRepository
from dataherald.eval import Evaluator
from dataherald.repositories.base import NLQueryResponseRepository
from dataherald.repositories.database_connections import DatabaseConnectionRepository
from dataherald.repositories.golden_records import GoldenRecordRepository
from dataherald.repositories.nl_question import NLQuestionRepository
from dataherald.sql_database.base import SQLDatabase, SQLInjectionError
from dataherald.sql_database.models.types import DatabaseConnection
from dataherald.sql_generator import SQLGenerator
from dataherald.sql_generator.generates_nl_answer import GeneratesNlAnswer
from dataherald.types import (
    DatabaseConnectionRequest,
    ExecuteTempQueryRequest,
    GoldenRecord,
    GoldenRecordRequest,
    NLQuery,
    NLQueryResponse,
    QuestionRequest,
    ScannerRequest,
    TableDescriptionRequest,
    UpdateQueryRequest,
)

logger = logging.getLogger(__name__)


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
    def scan_db(self, scanner_request: ScannerRequest) -> bool:
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
        try:
            scanner.scan(
                database,
                scanner_request.db_connection_id,
                scanner_request.table_names,
                DBScannerRepository(self.storage),
            )
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))  # noqa: B904
        return True

    @override
    def answer_question(self, question_request: QuestionRequest) -> NLQueryResponse:
        """Takes in an English question and answers it based on content from the registered databases"""
        logger.info(f"Answer question: {question_request.question}")
        sql_generation = self.system.instance(SQLGenerator)
        evaluator = self.system.instance(Evaluator)
        context_store = self.system.instance(ContextStore)

        user_question = NLQuery(
            question=question_request.question,
            db_connection_id=question_request.db_connection_id,
        )

        nl_question_repository = NLQuestionRepository(self.storage)
        user_question = nl_question_repository.insert(user_question)

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
                user_question, database_connection, context
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
        nl_query_response_repository = NLQueryResponseRepository(self.storage)
        nl_query_response = nl_query_response_repository.insert(generated_answer)
        return json.loads(json_util.dumps(nl_query_response))

    @override
    def create_database_connection(
        self, database_connection_request: DatabaseConnectionRequest
    ) -> DatabaseConnection:
        try:
            db_connection = DatabaseConnection(
                alias=database_connection_request.alias,
                uri=database_connection_request.connection_uri,
                path_to_credentials_file=database_connection_request.path_to_credentials_file,
                use_ssh=database_connection_request.use_ssh,
                ssh_settings=database_connection_request.ssh_settings,
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))  # noqa: B904
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
                use_ssh=database_connection_request.use_ssh,
                ssh_settings=database_connection_request.ssh_settings,
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))  # noqa: B904
        db_connection_repository = DatabaseConnectionRepository(self.storage)
        return db_connection_repository.update(db_connection)

    @override
    def update_table_description(
        self,
        table_description_id: str,
        table_description_request: TableDescriptionRequest,
    ) -> TableSchemaDetail:
        scanner_repository = DBScannerRepository(self.storage)
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
        self, db_connection_id: str | None = None, table_name: str | None = None
    ) -> list[TableSchemaDetail]:
        scanner_repository = DBScannerRepository(self.storage)
        return scanner_repository.find_by(
            {"db_connection_id": db_connection_id, "table_name": table_name}
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
    def update_nl_query_response(
        self, query_id: str, query: UpdateQueryRequest  # noqa: ARG002
    ) -> NLQueryResponse:
        nl_query_response_repository = NLQueryResponseRepository(self.storage)
        nl_question_repository = NLQuestionRepository(self.storage)
        nl_query_response = nl_query_response_repository.find_by_id(query_id)
        nl_question = nl_question_repository.find_by_id(
            nl_query_response.nl_question_id
        )
        if nl_query_response.sql_query.strip() != query.sql_query.strip():
            nl_query_response.sql_query = query.sql_query
            evaluator = self.system.instance(Evaluator)
            db_connection_repository = DatabaseConnectionRepository(self.storage)
            database_connection = db_connection_repository.find_by_id(
                nl_question.db_connection_id
            )
            if not database_connection:
                raise HTTPException(
                    status_code=404, detail="Database connection not found"
                )
            try:
                confidence_score = evaluator.get_confidence_score(
                    nl_question, nl_query_response, database_connection
                )
                nl_query_response.confidence_score = confidence_score
                generates_nl_answer = GeneratesNlAnswer(self.system, self.storage)
                nl_query_response = generates_nl_answer.execute(nl_query_response)
            except SQLInjectionError as e:
                raise HTTPException(status_code=404, detail=str(e)) from e
            nl_query_response_repository.update(nl_query_response)
        return json.loads(json_util.dumps(nl_query_response))

    @override
    def get_nl_query_response(
        self, query_request: ExecuteTempQueryRequest  # noqa: ARG002
    ) -> NLQueryResponse:
        nl_query_response_repository = NLQueryResponseRepository(self.storage)
        nl_query_response = nl_query_response_repository.find_by_id(
            query_request.query_id
        )
        nl_query_response.sql_query = query_request.sql_query
        try:
            generates_nl_answer = GeneratesNlAnswer(self.system, self.storage)
            nl_query_response = generates_nl_answer.execute(nl_query_response)
        except SQLInjectionError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e
        return json.loads(json_util.dumps(nl_query_response))

    @override
    def delete_golden_record(self, golden_record_id: str) -> dict:
        context_store = self.system.instance(ContextStore)
        status = context_store.remove_golden_records([golden_record_id])
        return {"status": status}

    @override
    def get_golden_records(self, page: int = 1, limit: int = 10) -> List[GoldenRecord]:
        golden_records_repository = GoldenRecordRepository(self.storage)
        all_records = golden_records_repository.find_all()
        # Calculate the start and end indices for pagination
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        return all_records[start_idx:end_idx]
