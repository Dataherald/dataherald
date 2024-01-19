from typing import Any, Dict

from langchain.schema import AgentFinish
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult


class OpenAILogProbsCallbackHandler(BaseCallbackHandler):
    """Callback Handler that tracks OpenAI logprobs."""

    tokens: []
    logprobs: []

    def __init__(self) -> None:
        super().__init__()
        self.tokens = []
        self.logprobs = []

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:  # noqa: ARG002
        for generation in response.generations:
            model_ouptut = generation[0]
            temp_tokens = []
            temp_logprobs = []
            logprobs = model_ouptut.generation_info["logprobs"]
            if logprobs is None:
                continue
            for token in logprobs["content"]:
                temp_tokens.append(token.get("token"))
                temp_logprobs.append(token.get("logprob"))
            self.tokens.append(temp_tokens)
            self.logprobs.append(temp_logprobs)

    def on_chain_end(
        self, outputs: Dict[str, Any], **kwargs: Any
    ) -> Any:  # noqa: ARG002
        """Run when chain ends running."""
        pass

    def on_tool_end(self, output: str, **kwargs: Any) -> Any:  # noqa: ARG002
        """Run when tool ends running."""
        pass

    def on_agent_finish(
        self, finish: AgentFinish, **kwargs: Any
    ) -> Any:  # noqa: ARG002
        """Run on agent end."""
        pass
