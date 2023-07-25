# from datetime import datetime add this later
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class NLQuery(BaseModel):
    id: str | None = Field(alias="_id")
    question: str
    db_alias: str


class NLQueryResponse(BaseModel):
    id: str | None = Field(alias="_id")
    nl_question_id: Any
    nl_response: str | None = None
    intermediate_steps: list[str] | None = None
    sql_query: str
    exec_time: float | None = None
    total_tokens: int | None = None
    total_cost: float | None = None
    golden_record: bool = False
    # date_entered: datetime = datetime.now() add this later


class DataDefinitionType(Enum):
    GOLDEN_SQL = "GOLDEN_SQL"
    BUSINESS_CONTEXT = "BUSINESS_CONTEXT"


class SupportedDatabase(Enum):
    POSTGRES = "POSTGRES"
    DATABRICKS = "DATABRICKS"
    SNOWFLAKE = "SNOWFLAKE"
    SQLSERVER = "SQLSERVER"
