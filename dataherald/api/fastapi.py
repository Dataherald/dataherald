import json
import logging
import time
from typing import List

from bson import json_util
from fastapi import HTTPException
from overrides import override

from dataherald.api import API
from dataherald.config import DBConnectionConfigSettings, System
from dataherald.context_store import ContextStore
from dataherald.db import DB
from dataherald.eval import Evaluation, Evaluator
from dataherald.smart_cache import SmartCache
from dataherald.sql_database.models.types import DatabaseConnection, SSHSettings
from dataherald.sql_generator import SQLGenerator
from dataherald.types import DataDefinitionType, NLQuery, NLQueryResponse

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
            alias="postgres", **DBConnectionConfigSettings().dict()
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
    def answer_question(self, question: str, db_alias: str) -> NLQueryResponse:
        """Takes in an English question and answers it based on content from the registered databases"""
        cache = self.system.instance(SmartCache)
        sql_generation = self.system.instance(SQLGenerator)
        evaluator = self.system.instance(Evaluator)
        context_store = self.system.instance(ContextStore)

        user_question = NLQuery(question=question, db_alias=db_alias)
        user_question.id = self.storage.insert_one(
            "nl_question", user_question.dict(exclude={"id"})
        )
        db_connection = self.storage.find_one(
            "database_connection", {"alias": db_alias}
        )
        if not db_connection:
            raise HTTPException(status_code=404, detail="Database connection not found")
        database_connection = DatabaseConnection(**db_connection)

        context = context_store.retrieve_context_for_question(user_question)
        start_generated_answer = time.time()

        generated_answer = cache.lookup(user_question.question)
        if generated_answer is None:
            generated_answer = sql_generation.generate_response(
                user_question, database_connection, context
            )
            if evaluator.is_acceptable_response(
                user_question, generated_answer, database_connection
            ):
                cache.add(question, generated_answer)
        generated_answer.exec_time = time.time() - start_generated_answer
        self.storage.insert_one(
            "nl_query_response", generated_answer.dict(exclude={"id"})
        )
        return json.loads(json_util.dumps(generated_answer))

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
