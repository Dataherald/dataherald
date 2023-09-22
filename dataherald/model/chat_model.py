import os
from typing import Any

from langchain.chat_models import ChatAnthropic, ChatGooglePalm, ChatOpenAI
from overrides import override

from dataherald.model import LLMModel
from dataherald.sql_database.models.types import DatabaseConnection
from dataherald.utils.encrypt import FernetEncrypt


class ChatModel(LLMModel):
    def __init__(self, system):
        super().__init__(system)
        self.model_name = os.environ.get("LLM_MODEL", "gpt-4-32k")
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        self.anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
        self.google_api_key = os.environ.get("GOOGLE_API_KEY")

    @override
    def get_model(
        self,
        database_connection: DatabaseConnection,
        model_family="openai",
        **kwargs: Any
    ) -> Any:
        if database_connection.llm_credentials is not None:
            fernet_encrypt = FernetEncrypt()
            api_key = fernet_encrypt.decrypt(
                database_connection.llm_credentials.api_key
            )
            if model_family == "openai":
                self.openai_api_key = api_key
            elif model_family == "anthropic":
                self.anthropic_api_key = api_key
            elif model_family == "google":
                self.google_api_key = api_key
        if self.openai_api_key:
            self.model = ChatOpenAI(
                model_name=self.model_name, openai_api_key=self.openai_api_key, **kwargs
            )
        elif self.anthropic_api_key:
            self.model = ChatAnthropic(
                model=self.model, anthropic_api_key=self.anthropic_api_key, **kwargs
            )
        elif self.google_api_key:
            self.model = ChatGooglePalm(
                model_name=self.model_name, google_api_key=self.google_api_key, **kwargs
            )
        else:
            raise ValueError("No valid API key environment variable found")
        return self.model
