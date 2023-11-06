import os
import time
from typing import List, Tuple

from overrides import override

from dataherald.sql_database.models.types import (
    DatabaseConnection,
)
from dataherald.sql_generator import SQLGenerator
from dataherald.types import Question, Response


class DataheraldFineTunedAgent(SQLGenerator):

    @override
    def generate_response(
        self,
        user_question: Question,
        database_connection: DatabaseConnection,
        context: Tuple[List[dict] | None, List[dict] | None],
    ) -> Response:
        start_time = time.time()
        instructions = context[1]
        
        self.short_context_llm = self.model.get_model(
            database_connection=database_connection,
            temperature=0,
            model_name=os.getenv("LLM_MODEL", "gpt-4"),
        )
        self.long_context_llm = self.model.get_model(
            database_connection=database_connection,
            temperature=0,
            model_name=os.getenv("AGENT_LLM_MODEL", "gpt-4-32k")
        )
