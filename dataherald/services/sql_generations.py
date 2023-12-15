from dataherald.api.types.requests import SQLGenerationRequest
from dataherald.repositories.sql_generations import SQLGenerationRepository
from dataherald.types import SQLGeneration


class SQLGenerationService:
    def __init__(self, storage):
        self.sql_generation_repository = SQLGenerationRepository(storage)

    def create(
        self, nl_generation_id: str, sql_generation_request: SQLGenerationRequest
    ) -> SQLGeneration:
        pass
