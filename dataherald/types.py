from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class NLQuery(BaseModel):
    id: str | None = Field(alias="_id")
    question: str


class NLQueryResponse(BaseModel):
    id: str | None = Field(alias="_id")
    nl_question_id: Any
    nl_response: str
    intermediate_steps: list[str]
    sql_query: str
    exec_time: float | None = None


class SupportedDatabase(Enum):
    POSTGRES = "POSTGRES"
    DATABRICKS = "DATABRICKS"
    SNOWFLAKE = "SNOWFLAKE"
    SQLSERVER = "SQLSERVER"
