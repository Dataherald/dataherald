import math
from typing import Any, Dict

from langchain.schema import AgentFinish
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult


class OpenAILogProbsCallbackHandler(BaseCallbackHandler):
    """Callback Handler that tracks OpenAI logprobs."""

    tokens: list[list[str]]
    probs: list[list[float]]

    def __init__(self) -> None:
        super().__init__()
        self.tokens = []
        self.probs = []

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:  # noqa: ARG002
        for generation in response.generations:
            model_ouptut = generation[0]
            temp_tokens = []
            temp_probs = []
            logprobs = model_ouptut.generation_info["logprobs"]
            if logprobs is None:
                continue
            for token in logprobs["content"]:
                top_token = token.get("token")
                top_token_prob = round(math.exp(token.get("logprob")), 3)
                for index, candidate in enumerate(token.get("top_logprobs")):
                    if index == 0:
                        continue
                    candidate_token = candidate.get("token")
                    candidate_prob = round(math.exp(candidate.get("logprob")), 3)
                    if (
                        top_token.strip().lower() in candidate_token.strip().lower()
                        or candidate_token.strip().lower() in top_token.strip().lower()
                    ):
                        top_token_prob += candidate_prob
                temp_tokens.append(top_token)
                temp_probs.append(top_token_prob)
            self.tokens.append(temp_tokens)
            self.probs.append(temp_probs)

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
