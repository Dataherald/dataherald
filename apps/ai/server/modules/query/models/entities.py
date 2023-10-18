from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, confloat

from modules.user.models.entities import SlackInfo


class Question(BaseModel):
    id: Any = Field(alias="_id")
    question: str
    db_connection_id: Any


class QueryStatus(str, Enum):
    NOT_VERIFIED = "NOT_VERIFIED"
    VERIFIED = "VERIFIED"
    SQL_ERROR = "SQL_ERROR"
    REJECTED = "REJECTED"


class SQLGenerationStatus(Enum):
    VALID = "VALID"
    INVALID = "INVALID"
    NONE = "NONE"


class Query(BaseModel):
    id: Any = Field(alias="_id")
    status: QueryStatus
    question_id: Any
    response_id: Any
    question_date: str
    last_updated: str
    updated_by: Any
    organization_id: Any
    display_id: str | None
    slack_info: SlackInfo
    custom_response: str | None


class SQLQueryResult(BaseModel):
    columns: list[str]
    rows: list[dict]


class BaseEngineAnswer(BaseModel):
    response: str | None
    intermediate_steps: list[str] | None
    sql_query: str | None
    sql_query_result: SQLQueryResult | None
    sql_generation_status: SQLGenerationStatus = "NONE"
    exec_time: float | None
    total_tokens: int | None
    total_cost: float | None
    confidence_score: confloat(ge=0, le=1) | None
    error_message: str | None


class EngineAnswer(BaseEngineAnswer):
    id: Any | None = Field(alias="_id")
    question_id: Any
