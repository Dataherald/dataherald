import os
from typing import Any

from langchain.llms import AlephAlpha, Anthropic, Cohere, OpenAI
from overrides import override

from dataherald.model import LLMModel
from dataherald.sql_database.models.types import DatabaseConnection
from dataherald.utils.encrypt import FernetEncrypt


class BaseModel(LLMModel):
    def __init__(self, system):
        super().__init__(system)
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        self.aleph_alpha_api_key = os.environ.get("ALEPH_ALPHA_API_KEY")
        self.anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
        self.cohere_api_key = os.environ.get("COHERE_API_KEY")

    @override
    def get_model(
        self,
        database_connection: DatabaseConnection,
        model_family="openai",
        model_name="davinci-003",
        **kwargs: Any
    ) -> Any:
        if database_connection.llm_api_key is not None:
            fernet_encrypt = FernetEncrypt()
            api_key = fernet_encrypt.decrypt(database_connection.llm_api_key)
            if model_family == "openai":
                self.openai_api_key = api_key
            elif model_family == "anthropic":
                self.anthropic_api_key = api_key
            elif model_family == "google":
                self.google_api_key = api_key
        if self.openai_api_key:
            self.model = OpenAI(model_name=model_name, **kwargs)
        elif self.aleph_alpha_api_key:
            self.model = AlephAlpha(model=model_name, **kwargs)
        elif self.anthropic_api_key:
            self.model = Anthropic(model=model_name, **kwargs)
        elif self.cohere_api_key:
            self.model = Cohere(model=model_name, **kwargs)
        else:
            raise ValueError("No valid API key environment variable found")
        return self.model
