from typing import Any

from pydantic import BaseModel


class NLQuery(BaseModel):
    id: Any
    question: str


class NLQueryResponse(BaseModel):
    id: Any
    nl_question_id: Any
    nl_response: str
    intermediate_steps: list[str]
    sql_query: str
    exec_time: float | None = None
