from dataherald.api.types.requests import PromptRequest
from dataherald.repositories.database_connections import (
    DatabaseConnectionNotFoundError,
    DatabaseConnectionRepository,
)
from dataherald.repositories.prompts import PromptRepository
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

        prompt = Prompt(
            text=prompt_request.text,
            db_connection_id=prompt_request.db_connection_id,
            metadata=prompt_request.metadata,
        )
        return self.prompt_repository.insert(prompt)

    def get(self, query) -> list[Prompt]:
        return self.prompt_repository.find_by(query)
