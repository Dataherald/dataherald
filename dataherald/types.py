# from datetime import datetime add this later
from enum import Enum
from typing import Any

from pydantic import BaseModel

from dataherald.sql_database.models.types import SSHSettings


class UpdateQueryRequest(BaseModel):
    sql_query: str


class ExecuteTempQueryRequest(BaseModel):
    sql_query: str


class SQLQueryResult(BaseModel):
    columns: list[str]
    rows: list[dict]


class NLQuery(BaseModel):
    id: Any
    question: str
    db_alias: str


class GoldenRecordRequest(BaseModel):
    question: str
    sql_query: str
    db_alias: str


class GoldenRecord(BaseModel):
    id: Any
    question: str
    sql_query: str
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
    confidence_score: float | None = None
    # date_entered: datetime = datetime.now() add this later


class ScannedDBTable(BaseModel):
    id: str
    name: str
    columns: list[str]


class ScannedDBResponse(BaseModel):
    db_alias: str
    tables: list[ScannedDBTable]


class SupportedDatabase(Enum):
    POSTGRES = "POSTGRES"
    DATABRICKS = "DATABRICKS"
    SNOWFLAKE = "SNOWFLAKE"
    SQLSERVER = "SQLSERVER"
    BIGQUERY = "BIGQUERY"


class QuestionRequest(BaseModel):
    question: str
    db_alias: str


class ScannerRequest(BaseModel):
    db_alias: str
    table_name: str | None


class DatabaseConnectionRequest(BaseModel):
    db_alias: str
    use_ssh: bool = False
    connection_uri: str | None
    path_to_credentials_file: str | None
    ssh_settings: SSHSettings | None


class ColumnDescriptionRequest(BaseModel):
    name: str
    description: str


class TableDescriptionRequest(BaseModel):
    description: str | None
    columns: list[ColumnDescriptionRequest] | None
