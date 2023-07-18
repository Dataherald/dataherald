"""A wrapper for the SQL generation functions in langchain"""

import logging

from langchain.agents import initialize_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.agents.agent_types import AgentType
from langchain.schema import AgentAction
from overrides import override

from dataherald.sql_database.base import SQLDatabase
from dataherald.sql_database.models.types import DatabaseConnection
from dataherald.sql_generator import SQLGenerator
from dataherald.types import NLQuery, NLQueryResponse

logger = logging.getLogger(__name__)


class LangChainSQLAgentSQLGenerator(SQLGenerator):
    @override
    def generate_response(
        self,
        user_question: NLQuery,
        database_connection: DatabaseConnection,
        context: str = None,
    ) -> NLQueryResponse:  # type: ignore
        logger.info(f"Generating SQL response to question: {str(user_question.dict())}")
        self.database = SQLDatabase.get_sql_engine(database_connection)
        tools = SQLDatabaseToolkit(db=self.database, llm=self.llm).get_tools()

        # builds a sql agent using initialize_agent instead of create_sql_agent to get intermediate steps in output
        # to create custom agent: https://python.langchain.com/docs/modules/agents/how_to/custom_llm_chat_agent
        agent_executor = initialize_agent(
            tools,
            self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            handle_parsing_errors=True,
            return_intermediate_steps=True,
        )

        question_with_context = (
            f"{user_question.question} An example of a similar question and the query that was generated \
                                to answer it is the following {context}"
            if context is not None
            else user_question.question
        )
        result = agent_executor(question_with_context)

        intermediate_steps = []
        sql_query_list = []
        for step in result["intermediate_steps"]:
            action = step[0]
            if type(action) == AgentAction and action.tool == "sql_db_query":
                sql_query_list.append(action.tool_input)

            intermediate_steps.append(str(step))

        return NLQueryResponse(
            nl_question_id=user_question.id,
            nl_response=result["output"],
            intermediate_steps=intermediate_steps,
            sql_query=sql_query_list[-1] if len(sql_query_list) > 0 else "",
        )
