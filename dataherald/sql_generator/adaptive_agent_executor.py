from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Union

from langchain.agents.agent import (
    AgentExecutor,
    BaseMultiActionAgent,
    BaseSingleActionAgent,
    ExceptionTool,
)
from langchain.agents.tools import InvalidTool
from langchain.callbacks.manager import CallbackManagerForChainRun, Callbacks
from langchain.schema import AgentAction, AgentFinish, OutputParserException
from langchain.tools.base import BaseTool
from overrides import override
from tiktoken.core import Encoding


class AdaptiveAgentExecutor(AgentExecutor):
    agent: Union[BaseSingleActionAgent, BaseMultiActionAgent]  # noqa: UP007
    tools: Sequence[BaseTool]
    return_intermediate_steps: bool = False
    max_iterations: Optional[int] = 15  # noqa: UP007
    max_execution_time: Optional[float] = None  # noqa: UP007
    early_stopping_method: str = "force"
    handle_parsing_errors: Union[  # noqa: UP007
        bool, str, Callable[[OutputParserException], str]
    ] = False
    trim_intermediate_steps: Union[  # noqa: UP007
        int, Callable[[List[Tuple[AgentAction, str]]], List[Tuple[AgentAction, str]]]
    ] = -1
    llm_list: dict
    switch_to_larger_model_threshold: int
    enc: Encoding
    tokens: int

    @classmethod
    def from_agent_and_tools(
        cls,
        agent: Union[BaseSingleActionAgent, BaseMultiActionAgent],  # noqa: UP007
        tools: Sequence[BaseTool],
        llm_list: dict,
        switch_to_larger_model_threshold: int,
        encoding: Encoding,
        callbacks: Callbacks = None,
        **kwargs: Any,
    ) -> AgentExecutor:
        """Create from agent and tools."""
        return cls(
            agent=agent,
            tools=tools,
            llm_list=llm_list,
            switch_to_larger_model_threshold=switch_to_larger_model_threshold,
            enc=encoding,
            callbacks=callbacks,
            tokens=len(encoding.encode(str(agent.llm_chain.prompt.template))),
            **kwargs,
        )

    def token_counter(self, intermediate_steps: List[Tuple[AgentAction, str]]) -> int:
        if len(intermediate_steps) == 0:
            return self.tokens
        new_item_text = (
            str(intermediate_steps[-1][0].log)
            + str(intermediate_steps[-1][0].tool)
            + str(intermediate_steps[-1][0].tool_input)
            + str(intermediate_steps[-1][1])
        )
        self.tokens += len(self.enc.encode(new_item_text))
        return self.tokens

    @override
    def _take_next_step(  # noqa: PLR0912 C901 PLR0915
        self,
        name_to_tool_map: Dict[str, BaseTool],
        color_mapping: Dict[str, str],
        inputs: Dict[str, str],
        intermediate_steps: List[Tuple[AgentAction, str]],
        run_manager: Optional[CallbackManagerForChainRun] = None,  # noqa: UP007
    ) -> Union[AgentFinish, List[Tuple[AgentAction, str]]]:  # noqa: UP007
        try:
            intermediate_steps = self._prepare_intermediate_steps(intermediate_steps)

            if self.agent.llm_chain.llm == self.llm_list["short_context_llm"]:
                if (
                    self.token_counter(intermediate_steps)
                    > self.switch_to_larger_model_threshold
                ):
                    self.agent.llm_chain.llm = self.llm_list["long_context_llm"]

            # Call the LLM to see what to do.
            output = self.agent.plan(
                intermediate_steps,
                callbacks=run_manager.get_child() if run_manager else None,
                **inputs,
            )
        except OutputParserException as e:
            if isinstance(self.handle_parsing_errors, bool):
                raise_error = not self.handle_parsing_errors
            else:
                raise_error = False
            if raise_error:
                raise ValueError(  # noqa: B904
                    "An output parsing error occurred. "
                    "In order to pass this error back to the agent and have it try "
                    "again, pass `handle_parsing_errors=True` to the AgentExecutor. "
                    f"This is the error: {str(e)}"
                )
            text = str(e)
            if isinstance(self.handle_parsing_errors, bool):
                if e.send_to_llm:
                    observation = str(e.observation)
                    text = str(e.llm_output)
                else:
                    observation = "Invalid or incomplete response"
            elif isinstance(self.handle_parsing_errors, str):
                observation = self.handle_parsing_errors
            elif callable(self.handle_parsing_errors):
                observation = self.handle_parsing_errors(e)
            else:
                raise ValueError(
                    "Got unexpected type of `handle_parsing_errors`"
                ) from e
            output = AgentAction("_Exception", observation, text)
            if run_manager:
                run_manager.on_agent_action(output, color="green")
            tool_run_kwargs = self.agent.tool_run_logging_kwargs()
            observation = ExceptionTool().run(
                output.tool_input,
                verbose=self.verbose,
                color=None,
                callbacks=run_manager.get_child() if run_manager else None,
                **tool_run_kwargs,
            )
            return [(output, observation)]
        # If the tool chosen is the finishing tool, then we end and return.
        if isinstance(output, AgentFinish):
            return output
        actions: List[AgentAction]
        if isinstance(output, AgentAction):
            actions = [output]
        else:
            actions = output
        result = []
        for agent_action in actions:
            if run_manager:
                run_manager.on_agent_action(agent_action, color="green")
            # Otherwise we lookup the tool
            if agent_action.tool in name_to_tool_map:
                tool = name_to_tool_map[agent_action.tool]
                return_direct = tool.return_direct
                color = color_mapping[agent_action.tool]
                tool_run_kwargs = self.agent.tool_run_logging_kwargs()
                if return_direct:
                    tool_run_kwargs["llm_prefix"] = ""
                # We then call the tool on the tool input to get an observation
                observation = tool.run(
                    agent_action.tool_input,
                    verbose=self.verbose,
                    color=color,
                    callbacks=run_manager.get_child() if run_manager else None,
                    **tool_run_kwargs,
                )
            else:
                tool_run_kwargs = self.agent.tool_run_logging_kwargs()
                observation = InvalidTool().run(
                    {
                        "requested_tool_name": agent_action.tool,
                        "available_tool_names": list(name_to_tool_map.keys()),
                    },
                    verbose=self.verbose,
                    color=None,
                    callbacks=run_manager.get_child() if run_manager else None,
                    **tool_run_kwargs,
                )
            result.append((agent_action, observation))
        return result
