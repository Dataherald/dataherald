from typing import Any

from pydantic import BaseModel, Field, confloat

from modules.query.models.entities import (
    QueryStatus,
    SQLGenerationStatus,
    SQLQueryResult,
)
from modules.user.models.entities import User


class CoreQueryResponse(BaseModel):
    id: Any | None = Field(alias="_id")
    nl_question_id: Any
    nl_response: str | None = None
    intermediate_steps: list[str] | None = None
    sql_query: str
    sql_query_result: SQLQueryResult | None
    sql_generation_status: SQLGenerationStatus = "NONE"
    exec_time: float | None = None
    total_tokens: int | None = None
    total_cost: float | None = None
    confidence_score: confloat(ge=0, le=1) | None = None
    error_message: str | None


class QuerySlackResponse(BaseModel):
    id: str
    display_id: str
    nl_response: str | None
    sql_query: str
    exec_time: float | None = None
    is_above_confidence_threshold: bool = False


class QueryListResponse(BaseModel):
    id: str
    username: str
    question: str
    question_date: str
    nl_response: str | None
    status: QueryStatus | None
    evaluation_score: float | None
    display_id: str | None


class QueryResponse(QueryListResponse):
    sql_query_result: SQLQueryResult | None
    sql_query: str
    ai_process: list[str] = ["process unknown"]
    last_updated: str | None
    updated_by: User | None
    sql_error_message: str | None
