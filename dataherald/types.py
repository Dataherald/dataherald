# from datetime import datetime add this later
from enum import Enum
from typing import Any

from pydantic import BaseModel


class UpdateQueryRequest(BaseModel):
    sql_query: str
    golden_record: bool


class ExecuteTempQueryRequest(BaseModel):
    sql_query: str


class SQLQueryResult(BaseModel):
    columns: list[str]
    rows: list[dict]


class ExecuteTempQueryResponse(BaseModel):
    nl_response: str | None = None
    sql_query_result: SQLQueryResult | None


class NLQuery(BaseModel):
    id: Any
    question: str
    db_alias: str


class SQLGenerationStatus(Enum):
    NONE = "NONE"
    VALID = "VALID"
    INVALID = "INVALID"


class NLQueryResponse(BaseModel):
    id: Any
    nl_question_id: Any
    nl_response: str | None = None
    intermediate_steps: list[str] | None = None
    sql_query: str
    sql_query_result: SQLQueryResult | None
    sql_generation_status: str = "NONE"
    error_message: str | None
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
