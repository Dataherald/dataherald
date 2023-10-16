import os
from typing import Any

from langchain.chat_models import ChatLiteLLM
from overrides import override

from dataherald.model import LLMModel
from dataherald.sql_database.models.types import DatabaseConnection
from dataherald.utils.encrypt import FernetEncrypt


class ChatModel(LLMModel):
    def __init__(self, system):
        super().__init__(system)

    @override
    def get_model(
        self,
        database_connection: DatabaseConnection,
        model_family="openai",
        model_name: str = "gpt-4-32k",
        **kwargs: Any
    ) -> Any:
        if database_connection.llm_credentials is not None:
            fernet_encrypt = FernetEncrypt()
            api_key = fernet_encrypt.decrypt(
                database_connection.llm_credentials.api_key
            )
            if model_family == "openai":
                os.environ["OPENAI_API_KEY"] = api_key
            elif model_family == "anthropic":
                os.environ["ANTHROPIC_API_KEY"] = api_key
            elif model_family == "google":
                os.environ["GOOGLE_API_KEY"] = api_key
            elif model_family == "cohere":
                os.environ["COHERE_API_KEY"] = api_key
        try:
            return ChatLiteLLM(model_name=model_name, **kwargs)
        except Exception as e:
            raise ValueError("No valid API key environment variable found") from e
