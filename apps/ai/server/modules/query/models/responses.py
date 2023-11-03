from pydantic import BaseModel

from modules.query.models.entities import BaseAnswer, QueryStatus, SQLQueryResult
from modules.user.models.responses import UserResponse


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
    question_date: str | None
    response: str | None
    status: QueryStatus | None
    evaluation_score: float | None
    display_id: str | None


class QueryResponse(QueryListResponse):
    question_id: str
    answer_id: str
    sql_query_result: SQLQueryResult | None
    sql_query: str
    ai_process: list[str] = []
    last_updated: str | None
    updated_by: UserResponse | None
    sql_error_message: str | None


class AnswerResponse(BaseAnswer):
    id: str
    question_id: str


class MessageResponse(BaseModel):
    message: str
