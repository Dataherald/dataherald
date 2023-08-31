from typing import Any

from pydantic import BaseModel, Field, confloat

from modules.k2_core.models.entities import SQLGenerationStatus, SQLQueryResult


class NLQueryResponse(BaseModel):
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


class NLQuerySlackResponse(BaseModel):
    id: str
    display_id: str
    nl_response: str
    sql_query: str
    exec_time: float | None = None
    is_above_confidence_threshold: bool = False
