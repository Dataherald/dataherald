from pydantic import BaseModel

from modules.query.models.entities import (
    BaseEngineAnswer,
    QueryStatus,
    SQLQueryResult,
)
from modules.user.models.responses import UserResponse


class EngineAnswerResponse(BaseEngineAnswer):
    id: str | None
    question_id: str


class QuerySlackResponse(BaseModel):
    id: str
    display_id: str
    response: str | None
    sql_query: str
    exec_time: float | None = None
    is_above_confidence_threshold: bool = False


class QueryListResponse(BaseModel):
    id: str
    username: str
    question: str
    question_date: str
    response: str | None
    status: QueryStatus | None
    evaluation_score: float | None
    display_id: str | None


class QueryResponse(QueryListResponse):
    sql_query_result: SQLQueryResult | None
    sql_query: str
    ai_process: list[str] = []
    last_updated: str | None
    updated_by: UserResponse | None
    sql_error_message: str | None
