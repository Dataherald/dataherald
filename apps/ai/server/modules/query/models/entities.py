from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from modules.user.models.entities import SlackInfo


class Question(BaseModel):
    id: Any = Field(alias="_id")
    question: str


class QueryStatus(Enum):
    NOT_VERIFIED = "NOT_VERIFIED"
    VERIFIED = "VERIFIED"
    SQL_ERROR = "SQL_ERROR"


class SQLGenerationStatus(Enum):
    VALID = "VALID"
    INVALID = "INVALID"
    NONE = "NONE"


class QueryRef(BaseModel):
    id: Any = Field(alias="_id")
    query_response_id: Any
    question_date: str
    last_updated: str
    updated_by: Any | None
    organization_id: Any
    display_id: str | None
    slack_info: SlackInfo


class SQLQueryResult(BaseModel):
    columns: list[str]
    rows: list[dict]
