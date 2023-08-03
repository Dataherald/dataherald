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
    NOT_VERIFIED = "NOT_VERIFIED"
    VERIFIED = "VERIFIED"
    SQL_ERROR = "SQL_ERROR"


class QueryRef(BaseModel):
    id: Any = Field(alias="_id")
    query_response_id: Any
    user: User
    question_date: str
    last_updated: str
