from datetime import datetime, timezone
from enum import Enum

from bson.errors import InvalidId
from bson.objectid import ObjectId
from pydantic import BaseModel, Field, validator

from dataherald.sql_database.models.types import FileStorage, SSHSettings


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
    sql_query: str | None = Field(None, min_length=3)


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
    instruction: str = Field(None, min_length=3)


class Instruction(BaseModel):
    id: str | None = None
    instruction: str
    db_connection_id: str


class GoldenRecordRequest(DBConnectionValidation):
    question: str = Field(None, min_length=3)
    sql_query: str = Field(None, min_length=3)


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
    csv_file_path: str | None
    sql_generation_status: str = "INVALID"
    error_message: str | None
    exec_time: float | None = None
    total_tokens: int | None = None
    total_cost: float | None = None
    confidence_score: float | None = None
    created_at: datetime = Field(default_factory=datetime.now)

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
    question: str = Field(None, min_length=3)


class ScannerRequest(DBConnectionValidation):
    table_names: list[str] | None


class DatabaseConnectionRequest(BaseModel):
    alias: str
    use_ssh: bool = False
    connection_uri: str | None
    path_to_credentials_file: str | None
    llm_api_key: str | None
    ssh_settings: SSHSettings | None
    file_storage: FileStorage | None


class ForeignKeyDetail(BaseModel):
    field_name: str
    reference_table: str


class ColumnDescriptionRequest(BaseModel):
    name: str
    description: str | None
    is_primary_key: bool | None
    data_type: str | None
    low_cardinality: bool | None
    categories: list[str] | None
    foreign_key: ForeignKeyDetail | None


class TableDescriptionRequest(BaseModel):
    description: str | None
    columns: list[ColumnDescriptionRequest] | None


class FineTuningStatus(Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    VALIDATING_FILES = "validating_files"


class BaseLLM(BaseModel):
    model_provider: str | None = None
    model_name: str | None = None
    model_parameters: dict[str, str] | None = None


class Finetuning(BaseModel):
    id: str | None = None
    alias: str | None = None
    db_connection_id: str | None = None
    status: str = "queued"
    error: str | None = None
    base_llm: BaseLLM | None = None
    finetuning_file_id: str | None = None
    finetuning_job_id: str | None = None
    model_id: str | None = None
    created_at: datetime = Field(default_factory=datetime.now)
    golden_records: list[str] | None = None
    metadata: dict[str, str] | None = None


class FineTuningRequest(BaseModel):
    db_connection_id: str
    alias: str
    base_llm: BaseLLM
    golden_records: list[str] | None = None
    metadata: dict[str, str] | None = None


class CancelFineTuningRequest(BaseModel):
    finetuning_id: str
    metadata: dict[str, str] | None = None
