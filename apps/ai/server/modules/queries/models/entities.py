from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class User(BaseModel):
    id: str
    name: str


class Question(BaseModel):
    id: Any = Field(alias="_id")
    question: str


class QueryStatus(Enum):
    SQL_ERROR = "SQL_ERROR"
    NOT_VERIFIED = "NOT_VERIFIED"
    VERIFIED = "VERIFIED"


class QueryRef(BaseModel):
    id: Any = Field(alias="_id")
    query_response_id: Any
    user: User
    question_date: str
    last_updated: str


class Query(BaseModel):
    id: Any = Field(alias="_id")
    nl_question_id: Any
    nl_response: str
    intermediate_steps: list[str]
    sql_query: str
    exec_time: float
    total_tokens: int
    total_cost: float
    golden_record: bool
