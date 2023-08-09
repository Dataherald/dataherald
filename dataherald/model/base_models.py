import os
from typing import Any

from langchain.llms import AlephAlpha, Anthropic, Cohere, OpenAI
from overrides import override

from dataherald.model import Model


class BaseModel(Model):
    def __init__(self, system):
        super().__init__(system)
        self.model_name = os.environ.get("MODEL_NAME")
        if self.model_name is None:
            raise ValueError("MODEL_NAME environment variable not set")
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        self.aleph_alpha_api_key = os.environ.get("ALEPH_ALPHA_API_KEY")
        self.anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
        self.cohere_api_key = os.environ.get("COHERE_API_KEY")

    @override
    def get_model(self, **kwargs: Any) -> Any:
        if self.openai_api_key:
            self.model = OpenAI(model_name=self.model_name, **kwargs)
        elif self.aleph_alpha_api_key:
            self.model = AlephAlpha(model=self.model_name, **kwargs)
        elif self.anthropic_api_key:
            self.model = Anthropic(model=self.model, **kwargs)
        elif self.cohere_api_key:
            self.model = Cohere(model=self.model, **kwargs)
        else:
            raise ValueError("No valid API key environment variable found")
        return self.model
