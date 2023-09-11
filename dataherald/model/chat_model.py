import os
from typing import Any

from langchain.chat_models import ChatLiteLLM
from overrides import override

from dataherald.model import LLMModel


class ChatModel(LLMModel):
    def __init__(self, system):
        super().__init__(system)
        self.model_name = os.environ.get("LLM_MODEL", "gpt-4-32k")
        self.api_keys = {
            "openai_api_key": os.environ.get("OPENAI_API_KEY"),
            "anthropic_api_key": os.environ.get("ANTHROPIC_API_KEY"),
            "google_api_key": os.environ.get("GOOGLE_API_KEY"),
            "cohere_api_key": os.environ.get("COHERE_API_KEY"),
        }

    @override
    def get_model(self, **kwargs: Any) -> Any:
        for _, api_key in self.api_keys.items():
            if api_key:
                self.model = ChatLiteLLM(model_name=self.model_name, **kwargs)
                return self.model

        raise ValueError("No valid API key environment variable found")
