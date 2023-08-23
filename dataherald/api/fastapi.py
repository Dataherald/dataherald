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
from dataherald.db_scanner.repository.base import DBScannerRepository
from dataherald.eval import Evaluator
from dataherald.repositories.base import NLQueryResponseRepository
from dataherald.repositories.golden_records import GoldenRecordRepository
from dataherald.repositories.nl_question import NLQuestionRepository
from dataherald.sql_database.base import SQLDatabase
from dataherald.sql_database.models.types import DatabaseConnection
from dataherald.sql_generator import SQLGenerator
from dataherald.sql_generator.generates_nl_answer import GeneratesNlAnswer
from dataherald.types import (
    DatabaseConnectionRequest,
    ExecuteTempQueryRequest,
    GoldenRecordRequest,
    NLQuery,
    NLQueryResponse,
    QuestionRequest,
    ScannedDBResponse,
    ScannedDBTable,
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
        """Takes a db_alias and scan all the tables columns"""
        db_connection = self.storage.find_one(
            "database_connection", {"alias": scanner_request.db_alias}
        )
        if not db_connection:
            raise HTTPException(status_code=404, detail="Database connection not found")
        database_connection = DatabaseConnection(**db_connection)
        try:
            database = SQLDatabase.get_sql_engine(database_connection)
        except Exception:
            raise HTTPException(  # noqa: B904
                status_code=400,
                detail=f"Unable to connect to db: {scanner_request.db_alias}",
            )

        scanner = self.system.instance(Scanner)
        try:
            scanner.scan(
                database,
                scanner_request.db_alias,
                scanner_request.table_name,
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
            question=question_request.question, db_alias=question_request.db_alias
        )

        nl_question_repository = NLQuestionRepository(self.storage)
        user_question = nl_question_repository.insert(user_question)

        db_connection = self.storage.find_one(
            "database_connection", {"alias": question_request.db_alias}
        )
        if not db_connection:
            raise HTTPException(status_code=404, detail="Database connection not found")
        database_connection = DatabaseConnection(**db_connection)

        context = context_store.retrieve_context_for_question(user_question, namespace=question_request.namespace)
        start_generated_answer = time.time()
        try:
            generated_answer = sql_generation.generate_response(
                user_question, database_connection, context
            )
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))  # noqa: B904
        logger.info("Starts evaluator...")
        confidence_score = evaluator.get_confidence_score(
            user_question, generated_answer, database_connection
        )
        generated_answer.confidence_score = confidence_score
        generated_answer.exec_time = time.time() - start_generated_answer
        nl_query_response_repository = NLQueryResponseRepository(self.storage)
        nl_query_response = nl_query_response_repository.insert(generated_answer)
        return json.loads(json_util.dumps(nl_query_response))

    @override
    def connect_database(
        self, database_connection_request: DatabaseConnectionRequest
    ) -> bool:
        try:
            db_connection = DatabaseConnection(
                uri=database_connection_request.connection_uri,
                alias=database_connection_request.db_alias,
                use_ssh=database_connection_request.use_ssh,
                ssh_settings=database_connection_request.ssh_settings,
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))  # noqa: B904
        self.storage.update_or_create(
            "database_connection",
            {"alias": database_connection_request.db_alias},
            db_connection.dict(),
        )
        return True

    @override
    def add_description(
        self,
        db_name: str,
        table_name: str,
        table_description_request: TableDescriptionRequest,
    ) -> bool:
        scanner_repository = DBScannerRepository(self.storage)
        table = scanner_repository.get_table_info(db_name, table_name)
        if table_description_request.description:
            table.description = table_description_request.description
        if table_description_request.columns:
            for column_request in table_description_request.columns:
                for column in table.columns:
                    if column_request.name == column.name:
                        column.description = column_request.description

        scanner_repository.update(table)
        return True

    @override
    def add_golden_records(self, namespace: str, golden_records: List[GoldenRecordRequest]) -> list[dict]:
        """Takes in a list of NL <> SQL pairs and stores them to be used in prompts to the LLM"""
        context_store = self.system.instance(ContextStore)
        context_store.add_golden_records(golden_records, namespace)
        return golden_records

    @override
    def execute_query(self, query: Query) -> tuple[str, dict]:
        """Executes a SQL query against the database and returns the results"""
        db_connection = self.storage.find_one(
            "database_connection", {"alias": query.db_alias}
        )
        if not db_connection:
            raise HTTPException(status_code=404, detail="Database connection not found")
        database_connection = DatabaseConnection(**db_connection)
        database = SQLDatabase.get_sql_engine(database_connection)
        print(type(database.run_sql(query.sql_statement)))
        return database.run_sql(query.sql_statement)

    @override
    def update_query(
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
            db_connection = self.storage.find_one(
                "database_connection", {"alias": nl_question.db_alias}
            )
            if not db_connection:
                raise HTTPException(
                    status_code=404, detail="Database connection not found"
                )
            database_connection = DatabaseConnection(**db_connection)
            confidence_score = evaluator.get_confidence_score(
                nl_question, nl_query_response, database_connection
            )
            nl_query_response.confidence_score = confidence_score
            generates_nl_answer = GeneratesNlAnswer(self.system, self.storage)
            nl_query_response = generates_nl_answer.execute(nl_query_response)
            nl_query_response_repository.update(nl_query_response)
        return json.loads(json_util.dumps(nl_query_response))

    @override
    def execute_temp_query(
        self, query_id: str, query: ExecuteTempQueryRequest  # noqa: ARG002
    ) -> NLQueryResponse:
        nl_query_response_repository = NLQueryResponseRepository(self.storage)
        nl_query_response = nl_query_response_repository.find_by_id(query_id)
        nl_query_response.sql_query = query.sql_query
        generates_nl_answer = GeneratesNlAnswer(self.system, self.storage)
        nl_query_response = generates_nl_answer.execute(nl_query_response)
        return json.loads(json_util.dumps(nl_query_response))

    @override
    def get_scanned_databases(self, db_alias: str) -> ScannedDBResponse:
        scanner_repository = DBScannerRepository(self.storage)
        tables = scanner_repository.get_all_tables_by_db(db_alias)
        process_tables = []
        for table in tables:
            process_tables.append(
                ScannedDBTable(
                    id=table.id,
                    name=table.table_name,
                    columns=[column.name for column in table.columns],
                )
            )
        scanned_db_response = ScannedDBResponse(
            db_alias=db_alias, tables=process_tables
        )
        return json.loads(json_util.dumps(scanned_db_response))

    @override
    def delete_golden_record(self,  namespace: str, golden_record_id: str) -> dict:
        context_store = self.system.instance(ContextStore)
        status = context_store.remove_golden_records([golden_record_id],namespace)
        return {"status": status}

    @override
    def get_golden_records(self, namespace: str,  page: int = 1, limit: int = 10) -> List[dict]:
        golden_records_repository = GoldenRecordRepository(self.storage)
        all_records = golden_records_repository.find_all(namespace=namespace)
        # Calculate the start and end indices for pagination
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        return all_records[start_idx:end_idx]
