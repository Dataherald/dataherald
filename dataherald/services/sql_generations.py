from datetime import datetime

from dataherald.api.types.requests import SQLGenerationRequest
from dataherald.config import System
from dataherald.eval import Evaluator
from dataherald.repositories.database_connections import DatabaseConnectionRepository
from dataherald.repositories.prompts import PromptNotFoundError, PromptRepository
from dataherald.repositories.sql_generations import SQLGenerationRepository
from dataherald.sql_database.base import SQLDatabase
from dataherald.sql_generator.create_sql_query_status import create_sql_query_status
from dataherald.sql_generator.dataherald_finetuning_agent import (
    DataheraldFinetuningAgent,
)
from dataherald.sql_generator.dataherald_sqlagent import DataheraldSQLAgent
from dataherald.types import SQLGeneration


class SQLGenerationService:
    def __init__(self, system: System, storage):
        self.system = system
        self.storage = storage
        self.sql_generation_repository = SQLGenerationRepository(storage)

    def create(
        self, prompt_id: str, sql_generation_request: SQLGenerationRequest
    ) -> SQLGeneration:
        prompt_repository = PromptRepository(self.storage)
        prompt = prompt_repository.find_by_id(prompt_id)
        if not prompt:
            raise PromptNotFoundError(f"Prompt {prompt_id} not found")
        db_connection_repository = DatabaseConnectionRepository(self.storage)
        db_connection = db_connection_repository.find_by_id(prompt.db_connection_id)
        database = SQLDatabase.get_sql_engine(db_connection)
        if sql_generation_request.sql is not None:
            sql_generation = SQLGeneration(
                prompt_id=prompt_id,
                model=sql_generation_request.model,
                sql=sql_generation_request.sql,
                completed_at=datetime.now(),
                tokens_used=0,
                created_at=datetime.now(),
            )
            sql_generation = create_sql_query_status(
                db=database, query=sql_generation.sql, sql_generation=sql_generation
            )
        else:  # noqa: PLR5501
            if (
                sql_generation_request.model is None
                or sql_generation_request.model == ""
            ):
                sql_generator = DataheraldSQLAgent(self.system)
            else:
                sql_generator = DataheraldFinetuningAgent(self.system)
                sql_generator.finetuned_llm_id = sql_generation_request.model
            sql_generation = sql_generator.generate_response(
                user_prompt=prompt, database_connection=db_connection
            )
        if sql_generation_request.evaluate:
            evaluator = self.system.instance(Evaluator)
            confidence_score = evaluator.get_confidence_score(
                user_prompt=prompt,
                sql_generation=sql_generation,
                database_connection=db_connection,
            )
            sql_generation.evaluate = sql_generation_request.evaluate
            sql_generation.confidence_score = confidence_score
        sql_generation.metadata = sql_generation_request.metadata
        return self.sql_generation_repository.insert(sql_generation)
