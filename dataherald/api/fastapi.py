import json
import logging
import time
from typing import List

from bson import json_util
from fastapi import HTTPException
from overrides import override
from sql_metadata import Parser

from dataherald.api import API
from dataherald.api.types import Query
from dataherald.config import DBConnectionConfigSettings, System
from dataherald.context_store import ContextStore
from dataherald.db import DB
from dataherald.db_scanner import Scanner
from dataherald.db_scanner.repository.base import DBScannerRepository
from dataherald.eval import Evaluation, Evaluator
from dataherald.repositories.base import NLQueryResponseRepository
from dataherald.repositories.nl_question import NLQuestionRepository
from dataherald.sql_database.base import SQLDatabase
from dataherald.sql_database.models.types import DatabaseConnection
from dataherald.sql_generator import SQLGenerator
from dataherald.sql_generator.generates_nl_answer import GeneratesNlAnswer
from dataherald.types import (
    DatabaseConnectionRequest,
    DataDefinitionRequest,
    EvaluationRequest,
    ExecuteTempQueryRequest,
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

        # stores a database connection
        self.create_first_db_connection()

    def create_first_db_connection(self):
        db_connection_setting = DatabaseConnection(
            alias="v2_real_estate", **DBConnectionConfigSettings().dict()
        )
        self.storage.update_or_create(
            "database_connection",
            {"alias": db_connection_setting.alias},
            db_connection_setting.dict(),
        )

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

        database = SQLDatabase.get_sql_engine(database_connection)
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

        context = context_store.retrieve_context_for_question(user_question)
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
    def evaluate_question(self, evaluation_request: EvaluationRequest) -> Evaluation:
        """Evaluates an English question within the registered Evaluator"""
        pass

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
    def add_data_definition(
        self, data_definition_request: DataDefinitionRequest
    ) -> bool:
        """Take in a URI to a document containing data definitions"""
        context_store = self.system.instance(ContextStore)
        return context_store.add_data_definition(
            data_definition_request.type, data_definition_request.uri
        )

    @override
    def add_golden_records(self, golden_records: List) -> bool:
        """Takes in a list of NL <> SQL pairs and stores them to be used in prompts to the LLM"""
        context_store = self.system.instance(ContextStore)
        return context_store.add_golden_records(golden_records)

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
        context_store = self.system.instance(ContextStore)
        nl_query_response = nl_query_response_repository.find_by_id(query_id)
        nl_question = nl_question_repository.find_by_id(
            nl_query_response.nl_question_id
        )
        nl_query_response.sql_query = query.sql_query
        nl_query_response.golden_record = query.golden_record
        if query.golden_record:
            nl_query_response.confidence_score = 1.0
            tables = Parser(nl_query_response.sql_query).tables
            context_store.vector_store.add_record(
                documents=nl_question.question,
                collection=context_store.golden_record_collection,
                metadata=[
                    {"tables_used": tables[0], "db_alias": nl_question.db_alias}
                ],  # this should be updated for multiple tables
                ids=[str(nl_query_response.nl_question_id)],
            )
        else:
            question_id = str(nl_query_response.nl_question_id)
            context_store.remove_golden_records([question_id])
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
