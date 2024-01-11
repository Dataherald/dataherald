from datetime import datetime

import pandas as pd

from dataherald.api.types.requests import SQLGenerationRequest
from dataherald.config import System
from dataherald.eval import Evaluator
from dataherald.repositories.database_connections import (
    DatabaseConnectionRepository,
)
from dataherald.repositories.prompts import PromptNotFoundError, PromptRepository
from dataherald.repositories.sql_generations import (
    SQLGenerationNotFoundError,
    SQLGenerationRepository,
)
from dataherald.sql_database.base import SQLDatabase
from dataherald.sql_generator.create_sql_query_status import create_sql_query_status
from dataherald.sql_generator.dataherald_finetuning_agent import (
    DataheraldFinetuningAgent,
)
from dataherald.sql_generator.dataherald_sqlagent import DataheraldSQLAgent
from dataherald.types import SQLGeneration


class SQLGenerationError(Exception):
    pass


class EmptySQLGenerationError(Exception):
    pass


class SQLGenerationService:
    def __init__(self, system: System, storage):
        self.system = system
        self.storage = storage
        self.sql_generation_repository = SQLGenerationRepository(storage)

    def update_error(self, sql_generation: SQLGeneration, error: str) -> SQLGeneration:
        sql_generation.error = error
        return self.sql_generation_repository.update(sql_generation)

    def create(
        self, prompt_id: str, sql_generation_request: SQLGenerationRequest
    ) -> SQLGeneration:
        initial_sql_generation = SQLGeneration(
            prompt_id=prompt_id,
            created_at=datetime.now(),
            metadata=sql_generation_request.metadata,
        )
        self.sql_generation_repository.insert(initial_sql_generation)
        prompt_repository = PromptRepository(self.storage)
        prompt = prompt_repository.find_by_id(prompt_id)
        if not prompt:
            self.update_error(initial_sql_generation, f"Prompt {prompt_id} not found")
            raise PromptNotFoundError(
                f"Prompt {prompt_id} not found", initial_sql_generation.id
            )
        db_connection_repository = DatabaseConnectionRepository(self.storage)
        db_connection = db_connection_repository.find_by_id(prompt.db_connection_id)
        database = SQLDatabase.get_sql_engine(db_connection)
        if sql_generation_request.sql is not None:
            sql_generation = SQLGeneration(
                prompt_id=prompt_id,
                sql=sql_generation_request.sql,
                tokens_used=0,
            )
            try:
                sql_generation = create_sql_query_status(
                    db=database, query=sql_generation.sql, sql_generation=sql_generation
                )
            except Exception as e:
                self.update_error(initial_sql_generation, str(e))
                raise SQLGenerationError(str(e), initial_sql_generation.id) from e
        else:
            if (
                sql_generation_request.finetuning_id is None
                or sql_generation_request.finetuning_id == ""
            ):
                sql_generator = DataheraldSQLAgent(self.system)
            else:
                sql_generator = DataheraldFinetuningAgent(self.system)
                sql_generator.finetuning_id = sql_generation_request.finetuning_id
                initial_sql_generation.finetuning_id = (
                    sql_generation_request.finetuning_id
                )
            try:
                sql_generation = sql_generator.generate_response(
                    user_prompt=prompt, database_connection=db_connection
                )
            except Exception as e:
                self.update_error(initial_sql_generation, str(e))
                raise SQLGenerationError(str(e), initial_sql_generation.id) from e
        if sql_generation_request.evaluate:
            evaluator = self.system.instance(Evaluator)
            confidence_score = evaluator.get_confidence_score(
                user_prompt=prompt,
                sql_generation=sql_generation,
                database_connection=db_connection,
            )
            initial_sql_generation.evaluate = sql_generation_request.evaluate
            initial_sql_generation.confidence_score = confidence_score
        initial_sql_generation.sql = sql_generation.sql
        initial_sql_generation.tokens_used = sql_generation.tokens_used
        initial_sql_generation.completed_at = datetime.now()
        initial_sql_generation.status = sql_generation.status
        initial_sql_generation.error = sql_generation.error
        return self.sql_generation_repository.update(initial_sql_generation)

    def get(self, query) -> list[SQLGeneration]:
        return self.sql_generation_repository.find_by(query)

    def execute(self, sql_generation_id: str, max_rows: int = 100) -> tuple[str, dict]:
        sql_generation = self.sql_generation_repository.find_by_id(sql_generation_id)
        if not sql_generation:
            raise SQLGenerationNotFoundError(
                f"SQL Generation {sql_generation_id} not found"
            )
        prompt_repository = PromptRepository(self.storage)
        prompt = prompt_repository.find_by_id(sql_generation.prompt_id)
        db_connection_repository = DatabaseConnectionRepository(self.storage)
        db_connection = db_connection_repository.find_by_id(prompt.db_connection_id)
        database = SQLDatabase.get_sql_engine(db_connection)
        return database.run_sql(sql_generation.sql, max_rows)

    def update_metadata(self, sql_generation_id, metadata_request) -> SQLGeneration:
        sql_generation = self.sql_generation_repository.find_by_id(sql_generation_id)
        if not sql_generation:
            raise SQLGenerationNotFoundError(
                f"Sql generation {sql_generation_id} not found"
            )
        sql_generation.metadata = metadata_request.metadata
        return self.sql_generation_repository.update(sql_generation)

    def create_dataframe(self, sql_generation_id):
        sql_generation = self.sql_generation_repository.find_by_id(sql_generation_id)
        if not sql_generation:
            raise SQLGenerationNotFoundError(
                f"Sql generation {sql_generation_id} not found"
            )
        prompt_repository = PromptRepository(self.storage)
        prompt = prompt_repository.find_by_id(sql_generation.prompt_id)
        db_connection_repository = DatabaseConnectionRepository(self.storage)
        db_connection = db_connection_repository.find_by_id(prompt.db_connection_id)
        database = SQLDatabase.get_sql_engine(db_connection)
        results = database.run_sql(sql_generation.sql)
        if results is None:
            raise EmptySQLGenerationError(
                f"Sql generation {sql_generation_id} is empty"
            )
        data = results[1]["result"]
        return pd.DataFrame(data)
