from dataherald.api.types.requests import NLGenerationRequest
from dataherald.repositories.nl_generations import NLGenerationRepository
from dataherald.types import NLGeneration


class NLGenerationService:
    def __init__(self, storage):
        self.nl_generation_repository = NLGenerationRepository(storage)

    def create(
        self, prompt_id: str, nl_generation_request: NLGenerationRequest
    ) -> NLGeneration:
        pass
