from datetime import datetime, timezone
from enum import Enum

from bson.errors import InvalidId
from bson.objectid import ObjectId
from pydantic import BaseModel, validator

from dataherald.sql_database.models.types import LLMCredentials, SSHSettings


class DBConnectionValidation(BaseModel):
    db_connection_id: str

    @validator("db_connection_id")
    def object_id_validation(cls, v: str):
        try:
            ObjectId(v)
        except InvalidId:
            raise ValueError("Must be a valid ObjectId")  # noqa: B904
        return v


class CreateResponseRequest(BaseModel):
    question_id: str
    sql_query: str


class SQLQueryResult(BaseModel):
    columns: list[str]
    rows: list[dict]


class Question(BaseModel):
    id: str | None = None
    question: str
    db_connection_id: str


class UpdateInstruction(BaseModel):
    instruction: str


class InstructionRequest(DBConnectionValidation):
    instruction: str


class Instruction(BaseModel):
    id: str | None = None
    instruction: str
    db_connection_id: str


class GoldenRecordRequest(DBConnectionValidation):
    question: str
    sql_query: str


class GoldenRecord(BaseModel):
    id: str | None = None
    question: str
    sql_query: str
    db_connection_id: str


class SQLGenerationStatus(Enum):
    NONE = "NONE"
    VALID = "VALID"
    INVALID = "INVALID"


class Response(BaseModel):
    id: str | None = None
    question_id: str | None = None
    response: str | None = None
    intermediate_steps: list[str] | None = None
    sql_query: str
    sql_query_result: SQLQueryResult | None
    sql_generation_status: str = "INVALID"
    error_message: str | None
    exec_time: float | None = None
    total_tokens: int | None = None
    total_cost: float | None = None
    confidence_score: float | None = None
    created_at: datetime = datetime.now()

    @validator("created_at", pre=True)
    def parse_datetime_with_timezone(cls, value):
        if not value:
            return None
        return value.replace(tzinfo=timezone.utc)  # Set the timezone to UTC

    @validator("question_id", pre=True)
    def parse_question_id(cls, value):
        return str(value)


class SupportedDatabase(Enum):
    POSTGRES = "POSTGRES"
    DATABRICKS = "DATABRICKS"
    SNOWFLAKE = "SNOWFLAKE"
    SQLSERVER = "SQLSERVER"
    BIGQUERY = "BIGQUERY"


class QuestionRequest(DBConnectionValidation):
    question: str


class ScannerRequest(DBConnectionValidation):
    table_names: list[str] | None


class DatabaseConnectionRequest(BaseModel):
    alias: str
    use_ssh: bool = False
    connection_uri: str | None
    path_to_credentials_file: str | None
    llm_credentials: LLMCredentials | None
    ssh_settings: SSHSettings | None


class ColumnDescriptionRequest(BaseModel):
    name: str
    description: str


class TableDescriptionRequest(BaseModel):
    description: str | None
    columns: list[ColumnDescriptionRequest] | None
