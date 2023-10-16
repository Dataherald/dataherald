import os
from typing import Any

from langchain.chat_models import ChatAnthropic, ChatCohere, ChatGooglePalm, ChatOpenAI
from overrides import override

from dataherald.model import LLMModel
from dataherald.sql_database.models.types import DatabaseConnection
from dataherald.utils.encrypt import FernetEncrypt


class ChatModel(LLMModel):
    def __init__(self, system):
        super().__init__(system)
        self.model_name = os.environ.get("LLM_MODEL", "gpt-4-32k")

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
                os.environ["OPENAI_API_KEY"] = api_key
            elif model_family == "anthropic":
                os.environ["ANTHROPIC_API_KEY"] = api_key
            elif model_family == "google":
                os.environ["GOOGLE_API_KEY"] = api_key
            elif model_family == "cohere":
                os.environ["COHERE_API_KEY"] = api_key
        if os.environ.get("OPENAI_API_KEY") is not None:
            return ChatOpenAI(model_name=self.model_name, **kwargs)
        if os.environ.get("ANTHROPIC_API_KEY") is not None:
            return ChatAnthropic(model_name=self.model_name, **kwargs)
        if os.environ.get("GOOGLE_API_KEY") is not None:
            return ChatGooglePalm(model_name=self.model_name, **kwargs)
        if os.environ.get("COHERE_API_KEY") is not None:
            return ChatCohere(model_name=self.model_name, **kwargs)
        raise ValueError("No valid API key environment variable found")
