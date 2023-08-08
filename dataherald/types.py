# from datetime import datetime add this later
from enum import Enum
from typing import Any

from pydantic import BaseModel

from dataherald.sql_database.models.types import SSHSettings


class UpdateQueryRequest(BaseModel):
    sql_query: str
    golden_record: bool


class ExecuteTempQueryRequest(BaseModel):
    sql_query: str


class SQLQueryResult(BaseModel):
    columns: list[str]
    rows: list[dict]


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
    confidence_score: float | None = None
    # date_entered: datetime = datetime.now() add this later


class DataDefinitionType(Enum):
    GOLDEN_SQL = "GOLDEN_SQL"
    BUSINESS_CONTEXT = "BUSINESS_CONTEXT"


class SupportedDatabase(Enum):
    POSTGRES = "POSTGRES"
    DATABRICKS = "DATABRICKS"
    SNOWFLAKE = "SNOWFLAKE"
    SQLSERVER = "SQLSERVER"


class QuestionRequest(BaseModel):
    question: str
    db_alias: str


class ScannerRequest(BaseModel):
    db_alias: str
    table_name: str | None


class EvaluationRequest(BaseModel):
    question: str
    golden_sql: str


class DatabaseConnectionRequest(BaseModel):
    db_alias: str
    use_ssh: bool
    connection_uri: str | None
    ssh_settings: SSHSettings | None


class DataDefinitionRequest(BaseModel):
    uri: str
    type: DataDefinitionType
