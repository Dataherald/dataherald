from dataherald.api.types.requests import NLGenerationRequest
from dataherald.config import System
from dataherald.repositories.nl_generations import NLGenerationRepository
from dataherald.repositories.sql_generations import (
    SQLGenerationNotFoundError,
    SQLGenerationRepository,
)
from dataherald.sql_generator.generates_nl_answer import GeneratesNlAnswer
from dataherald.types import NLGeneration


class NLGenerationService:
    def __init__(self, system: System, storage):
        self.system = system
        self.storage = storage
        self.nl_generation_repository = NLGenerationRepository(storage)

    def create(
        self, sql_generation_id: str, nl_generation_request: NLGenerationRequest
    ) -> NLGeneration:
        sql_generation_repository = SQLGenerationRepository(self.storage)
        sql_generation = sql_generation_repository.find_by_id(sql_generation_id)
        if not sql_generation:
            raise SQLGenerationNotFoundError(
                f"SQL Generation {sql_generation_id} not found"
            )
        nl_generator = GeneratesNlAnswer(self.system, self.storage)
        nl_generation = nl_generator.execute(
            sql_generation=sql_generation,
            top_k=nl_generation_request.max_rows,
        )
        nl_generation.metadata = nl_generation_request.metadata
        return self.nl_generation_repository.insert(nl_generation)
