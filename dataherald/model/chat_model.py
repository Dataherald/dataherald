import os
from typing import Any

from langchain.chat_models import ChatAnthropic, ChatGooglePalm, ChatOpenAI, ChatLiteLLM
from overrides import override

from dataherald.model import LLMModel


class ChatModel(LLMModel):
    def __init__(self, system):
        super().__init__(system)
        self.model_name = os.environ.get("LLM_MODEL", "gpt-4-32k")
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        self.anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
        self.google_api_key = os.environ.get("GOOGLE_API_KEY")

    @override
    def get_model(self, **kwargs: Any) -> Any:
        if self.openai_api_key:
            self.model = ChatLiteLLM(model_name=self.model_name, **kwargs)
        elif self.anthropic_api_key:
            self.model = ChatLiteLLM(model=self.model, **kwargs)
        elif self.google_api_key:
            self.model = ChatLiteLLM(model_name=self.model_name, **kwargs)
        else:
            raise ValueError("No valid API key environment variable found")
        return self.model
