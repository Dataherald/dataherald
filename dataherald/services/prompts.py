from dataherald.api.types.requests import PromptRequest
from dataherald.repositories.prompts import PromptRepository
from dataherald.types import Prompt


class PromptService:
    def __init__(self, storage):
        self.prompt_repository = PromptRepository(storage)

    def create(self, prompt_request: PromptRequest) -> Prompt:
        pass
