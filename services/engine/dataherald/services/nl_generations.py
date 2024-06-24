from datetime import datetime

from dataherald.api.types.requests import NLGenerationRequest
from dataherald.config import System
from dataherald.repositories.nl_generations import (
    NLGenerationNotFoundError,
    NLGenerationRepository,
)
from dataherald.repositories.sql_generations import (
    SQLGenerationNotFoundError,
    SQLGenerationRepository,
)
from dataherald.sql_generator.generates_nl_answer import GeneratesNlAnswer
from dataherald.types import LLMConfig, NLGeneration


class NLGenerationError(Exception):
    pass


class NLGenerationService:
    def __init__(self, system: System, storage):
        self.system = system
        self.storage = storage
        self.nl_generation_repository = NLGenerationRepository(storage)

    def create(
        self, sql_generation_id: str, nl_generation_request: NLGenerationRequest
    ) -> NLGeneration:
        initial_nl_generation = NLGeneration(
            sql_generation_id=sql_generation_id,
            created_at=datetime.now(),
            llm_config=(
                nl_generation_request.llm_config
                if nl_generation_request.llm_config
                else LLMConfig()
            ),
            metadata=nl_generation_request.metadata,
        )
        self.nl_generation_repository.insert(initial_nl_generation)
        sql_generation_repository = SQLGenerationRepository(self.storage)
        sql_generation = sql_generation_repository.find_by_id(sql_generation_id)
        if not sql_generation:
            raise SQLGenerationNotFoundError(
                f"SQL Generation {sql_generation_id} not found",
                initial_nl_generation.id,
            )
        nl_generator = GeneratesNlAnswer(
            self.system,
            self.storage,
            (
                nl_generation_request.llm_config
                if nl_generation_request.llm_config
                else LLMConfig()
            ),
        )
        try:
            nl_generation = nl_generator.execute(
                sql_generation=sql_generation,
                top_k=nl_generation_request.max_rows,
            )
        except Exception as e:
            raise NLGenerationError(str(e), initial_nl_generation.id) from e
        initial_nl_generation.text = nl_generation.text
        return self.nl_generation_repository.update(initial_nl_generation)

    def get(self, query) -> list[NLGeneration]:
        return self.nl_generation_repository.find_by(query)

    def update_metadata(self, nl_generation_id, metadata_request) -> NLGeneration:
        nl_generation = self.nl_generation_repository.find_by_id(nl_generation_id)
        if not nl_generation:
            raise NLGenerationNotFoundError(
                f"NL generation {nl_generation_id} not found"
            )
        nl_generation.metadata = metadata_request.metadata
        return self.nl_generation_repository.update(nl_generation)
