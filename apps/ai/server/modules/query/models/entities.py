from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# temporary placemnent, will need to move to the module that relates with user authentication
class User(BaseModel):
    id: str
    name: str


# temporary placemnent, will need to move to the module that relates with user authentication
class SlackQuestionUser(BaseModel):
    slack_id: str
    username: str


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
    user: SlackQuestionUser
    question_date: str
    last_updated: str
