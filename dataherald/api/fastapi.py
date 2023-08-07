import json
import logging
import time
from typing import List

from bson import json_util
from fastapi import HTTPException
from overrides import override

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
from dataherald.smart_cache import SmartCache
from dataherald.sql_database.base import SQLDatabase
from dataherald.sql_database.models.types import DatabaseConnection, SSHSettings
from dataherald.sql_generator import SQLGenerator
from dataherald.sql_generator.generates_nl_answer import GeneratesNlAnswer
from dataherald.types import (
    DataDefinitionType,
    ExecuteTempQueryRequest,
    NLQuery,
    NLQueryResponse,
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
    def scan_db(self, db_alias: str, table_name: str | None = None) -> bool:
        """Takes a db_alias and scan all the tables columns"""
        db_connection = self.storage.find_one(
            "database_connection", {"alias": db_alias}
        )
        if not db_connection:
            raise HTTPException(status_code=404, detail="Database connection not found")
        database_connection = DatabaseConnection(**db_connection)

        database = SQLDatabase.get_sql_engine(database_connection)
        scanner = self.system.instance(Scanner)
        try:
            scanner.scan(
                database, db_alias, table_name, DBScannerRepository(self.storage)
            )
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))  # noqa: B904
        return True

    @override
    def answer_question(self, question: str, db_alias: str) -> NLQueryResponse:
        """Takes in an English question and answers it based on content from the registered databases"""
        logger.info(f"Answer question: {question}")
        cache = self.system.instance(SmartCache)
        sql_generation = self.system.instance(SQLGenerator)
        evaluator = self.system.instance(Evaluator)
        context_store = self.system.instance(ContextStore)

        user_question = NLQuery(question=question, db_alias=db_alias)

        nl_question_repository = NLQuestionRepository(self.storage)
        user_question = nl_question_repository.insert(user_question)

        db_connection = self.storage.find_one(
            "database_connection", {"alias": db_alias}
        )
        if not db_connection:
            raise HTTPException(status_code=404, detail="Database connection not found")
        database_connection = DatabaseConnection(**db_connection)

        context = context_store.retrieve_context_for_question(user_question)
        start_generated_answer = time.time()

        generated_answer = cache.lookup(user_question.question + db_alias)
        if generated_answer is None:
            generated_answer = sql_generation.generate_response(
                user_question, database_connection, context
            )

            logger.info("Starts evaluator...")
            confidence_score = evaluator.get_confidence_score(
                user_question, generated_answer, database_connection
            )
            if confidence_score >= evaluator.acceptance_threshold:
                cache.add(question + db_alias, generated_answer)
            generated_answer.confidence_score = confidence_score
        generated_answer.exec_time = time.time() - start_generated_answer
        nl_query_response_repository = NLQueryResponseRepository(self.storage)
        nl_query_response = nl_query_response_repository.insert(generated_answer)
        return json.loads(json_util.dumps(nl_query_response))

    @override
    def evaluate_question(self, question: str, golden_sql: str) -> Evaluation:
        """Evaluates an English question within the registered Evaluator"""
        pass

    @override
    def connect_database(
        self,
        alias: str,
        use_ssh: bool,
        connection_uri: str | None = None,
        ssh_settings: SSHSettings | None = None,
    ) -> bool:
        try:
            db_connection = DatabaseConnection(
                uri=connection_uri,
                alias=alias,
                use_ssh=use_ssh,
                ssh_settings=ssh_settings,
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))  # noqa: B904
        self.storage.update_or_create(
            "database_connection", {"alias": alias}, db_connection.dict()
        )
        return True

    def add_data_definition(self, type: DataDefinitionType, uri: str) -> bool:
        """Take in a URI to a document containing data definitions"""
        context_store = self.system.instance(ContextStore)
        return context_store.add_data_definition(type, uri)

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
        nl_question = nl_question_repository.find_by_id(nl_query_response.nl_question_id)
        nl_query_response.sql_query = query.sql_query
        nl_query_response.golden_record = query.golden_record
        generates_nl_answer = GeneratesNlAnswer(self.storage)
        nl_query_response = generates_nl_answer.execute(nl_query_response)
        nl_query_response_repository.update(nl_query_response)
        golden_record = {"nl_question":nl_question.question,"sql": nl_query_response.sql_query, "db": nl_question.db_alias}
        added_to_context_store = context_store.add_golden_records([golden_record])
        if not added_to_context_store:
            raise HTTPException(
                status_code=500,
                detail="Could not add golden record to context store",
            )
        return json.loads(json_util.dumps(nl_query_response))

    @override
    def execute_temp_query(
        self, query_id: str, query: ExecuteTempQueryRequest  # noqa: ARG002
    ) -> NLQueryResponse:
        nl_query_response_repository = NLQueryResponseRepository(self.storage)
        nl_query_response = nl_query_response_repository.find_by_id(query_id)
        nl_query_response.sql_query = query.sql_query
        generates_nl_answer = GeneratesNlAnswer(self.storage)
        nl_query_response = generates_nl_answer.execute(nl_query_response)
        return json.loads(json_util.dumps(nl_query_response))
