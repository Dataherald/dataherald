from typing import Any

from pydantic import BaseModel


class NLQuery(BaseModel):
    id: Any
    question: str


class NLQueryResponse(BaseModel):
    id: Any
    nl_question_id: Any
    table_response: list[dict[str, Any]]
    nl_response: str
    tables_used: list[str]
    sql: str
    exec_time: float | None = None
