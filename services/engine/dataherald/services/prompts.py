from dataherald.api.types.requests import PromptRequest
from dataherald.repositories.database_connections import (
    DatabaseConnectionNotFoundError,
    DatabaseConnectionRepository,
)
from dataherald.repositories.prompts import PromptNotFoundError, PromptRepository
from dataherald.sql_database.services.database_connection import SchemaNotSupportedError
from dataherald.types import Prompt


class PromptService:
    def __init__(self, storage):
        self.storage = storage
        self.prompt_repository = PromptRepository(self.storage)

    def create(self, prompt_request: PromptRequest) -> Prompt:
        db_connection_repository = DatabaseConnectionRepository(self.storage)
        db_connection = db_connection_repository.find_by_id(
            prompt_request.db_connection_id
        )
        if not db_connection:
            raise DatabaseConnectionNotFoundError(
                f"Database connection {prompt_request.db_connection_id} not found"
            )

        if not db_connection.schemas and prompt_request.schemas:
            raise SchemaNotSupportedError(
                "Schema not supported for this db",
                description=f"The {db_connection.dialect} dialect doesn't support schemas",
            )

        prompt = Prompt(
            text=prompt_request.text,
            db_connection_id=prompt_request.db_connection_id,
            schemas=prompt_request.schemas,
            metadata=prompt_request.metadata,
        )
        return self.prompt_repository.insert(prompt)

    def get(self, query) -> list[Prompt]:
        return self.prompt_repository.find_by(query)

    def update_metadata(self, prompt_id, metadata_request) -> Prompt:
        prompt = self.prompt_repository.find_by_id(prompt_id)
        if not prompt:
            raise PromptNotFoundError(f"Prompt {prompt_id} not found")
        prompt.metadata = metadata_request.metadata
        return self.prompt_repository.update(prompt)
