from typing import Any

from langchain_community.chat_models import ChatAnthropic, ChatCohere, ChatGooglePalm
from langchain_openai import ChatOpenAI
from overrides import override

from dataherald.model import LLMModel
from dataherald.sql_database.models.types import DatabaseConnection


class ChatModel(LLMModel):
    def __init__(self, system):
        super().__init__(system)

    @override
    def get_model(
        self,
        database_connection: DatabaseConnection,
        model_family="openai",
        model_name="gpt-4-turbo-preview",
        api_base: str | None = None,
        **kwargs: Any
    ) -> Any:
        api_key = database_connection.decrypt_api_key()
        if model_family == "openai":
            return ChatOpenAI(
                model_name=model_name,
                openai_api_key=api_key,
                openai_api_base=api_base,
                **kwargs
            )
        if model_family == "anthropic":
            return ChatAnthropic(
                model_name=model_name, anthropic_api_key=api_key, **kwargs
            )
        if model_family == "google":
            return ChatGooglePalm(
                model_name=model_name, google_api_key=api_key, **kwargs
            )
        if model_family == "cohere":
            return ChatCohere(model_name=model_name, cohere_api_key=api_key, **kwargs)
        raise ValueError("No valid API key environment variable found")
