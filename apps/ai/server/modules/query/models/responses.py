from pydantic import BaseModel

from modules.k2_core.models.entities import SQLQueryResult
from modules.query.models.entities import QueryStatus


class QueryResponse(BaseModel):
    id: str
    username: str
    question: str
    question_date: str
    nl_response: str | None
    sql_query_result: SQLQueryResult | None
    sql_query: str
    ai_process: list[str]
    last_updated: str
    status: QueryStatus | None
    evaluation_score: float | None
    sql_error_message: str | None


class QueryListResponse(BaseModel):
    id: str
    username: str
    question: str
    question_date: str
    nl_response: str | None
    status: QueryStatus | None
    evaluation_score: float | None
