"""A wrapper for the SQL generation functions in langchain"""

import logging

from langchain.agents import initialize_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.agents.agent_types import AgentType
from langchain.schema import AgentAction
from overrides import override

from dataherald.sql_generator import SQLGenerator
from dataherald.types import NLQuery, NLQueryResponse

logger = logging.getLogger(__name__)


class LangChainSQLAgentSQLGenerator(SQLGenerator):
    def _handle_error(self, error) -> str:
        return error

    @override
    def generate_response(self, user_question: NLQuery) -> NLQueryResponse:
        logger.info("Generating SQL response to question: " + user_question.dict())

        db = self.database.from_uri(self.database.uri)

        tools = SQLDatabaseToolkit(db=db, llm=self.llm).get_tools()

        # builds a sql agent using initialize_agent instead of create_sql_agent to get intermediate steps in output
        # to create custom agent: https://python.langchain.com/docs/modules/agents/how_to/custom_llm_chat_agent
        agent_executor = initialize_agent(
            tools,
            self.llm,
            agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=self._handle_error,
            return_intermediate_steps=True,
        )

        result = agent_executor(user_question)

        intermediate_steps = []
        sql_query_list = []
        for step in result["intermediate_steps"]:
            action = step[0]
            if type(action) == AgentAction and action.tool == "query_sql_db":
                sql_query_list.append(action.tool_input)

            intermediate_steps.append(str(step))

        return NLQueryResponse(
            nl_question_id=user_question.id,
            nl_response=result["output"],
            intermediate_steps=intermediate_steps,
            sql_query=sql_query_list[-1] if len(sql_query_list) > 0 else "",
        )
