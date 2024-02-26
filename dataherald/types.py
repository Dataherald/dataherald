import os
from datetime import datetime
from enum import Enum

from bson.errors import InvalidId
from bson.objectid import ObjectId
from pydantic import BaseModel, Field, validator

from dataherald.sql_database.models.types import FileStorage, SSHSettings
from dataherald.utils.models_context_window import OPENAI_FINETUNING_MODELS_WINDOW_SIZES


class DBConnectionValidation(BaseModel):
    db_connection_id: str

    @validator("db_connection_id")
    def object_id_validation(cls, v: str):
        try:
            ObjectId(v)
        except InvalidId:
            raise ValueError("Must be a valid ObjectId")  # noqa: B904
        return v


class SQLQueryResult(BaseModel):
    columns: list[str]
    rows: list[dict]


class UpdateInstruction(BaseModel):
    instruction: str
    metadata: dict | None


class InstructionRequest(DBConnectionValidation):
    instruction: str = Field(None, min_length=3)
    metadata: dict | None


class RefreshTableDescriptionRequest(DBConnectionValidation):
    pass


class Instruction(BaseModel):
    id: str | None = None
    instruction: str
    db_connection_id: str
    created_at: datetime = Field(default_factory=datetime.now)
    metadata: dict | None


class GoldenSQLRequest(DBConnectionValidation):
    prompt_text: str = Field(None, min_length=3)
    sql: str = Field(None, min_length=3)
    metadata: dict | None


class GoldenSQL(BaseModel):
    id: str | None = None
    prompt_text: str
    sql: str
    db_connection_id: str
    created_at: datetime = Field(default_factory=datetime.now)
    metadata: dict | None


class SQLGenerationStatus(Enum):
    NONE = "NONE"
    VALID = "VALID"
    INVALID = "INVALID"


class SupportedDatabase(Enum):
    POSTGRES = "POSTGRES"
    DATABRICKS = "DATABRICKS"
    SNOWFLAKE = "SNOWFLAKE"
    SQLSERVER = "SQLSERVER"
    BIGQUERY = "BIGQUERY"


class ScannerRequest(DBConnectionValidation):
    table_names: list[str] | None
    metadata: dict | None


class DatabaseConnectionRequest(BaseModel):
    alias: str
    use_ssh: bool = False
    connection_uri: str
    path_to_credentials_file: str | None
    llm_api_key: str | None
    ssh_settings: SSHSettings | None
    file_storage: FileStorage | None
    metadata: dict | None


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
    metadata: dict | None


class FineTuningStatus(Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    VALIDATING_FILES = "VALIDATING_FILES"


class BaseLLM(BaseModel):
    model_provider: str | None = None
    model_name: str | None = None
    model_parameters: dict[str, str] | None = None

    @validator("model_name")
    def validate_model_name(cls, v: str | None):
        if v and v not in OPENAI_FINETUNING_MODELS_WINDOW_SIZES:
            raise ValueError(f"Model {v} not supported")  # noqa: B904
        return v


class Finetuning(BaseModel):
    id: str | None = None
    alias: str | None = None
    db_connection_id: str | None = None
    status: str = "QUEUED"
    error: str | None = None
    base_llm: BaseLLM | None = None
    finetuning_file_id: str | None = None
    finetuning_job_id: str | None = None
    model_id: str | None = None
    created_at: datetime = Field(default_factory=datetime.now)
    golden_sqls: list[str] | None = None
    metadata: dict | None


class FineTuningRequest(BaseModel):
    db_connection_id: str
    alias: str | None = None
    base_llm: BaseLLM | None = None
    golden_sqls: list[str] | None = None
    metadata: dict | None


class CancelFineTuningRequest(BaseModel):
    finetuning_id: str
    metadata: dict | None


class Prompt(BaseModel):
    id: str | None = None
    text: str
    db_connection_id: str
    created_at: datetime = Field(default_factory=datetime.now)
    metadata: dict | None


class LLMConfig(BaseModel):
    llm_name: str = os.getenv("LLM_NAME", "gpt-4-turbo-preview")
    api_base: str | None = None


class SQLGeneration(BaseModel):
    id: str | None = None
    prompt_id: str
    finetuning_id: str | None
    low_latency_mode: bool = False
    llm_config: LLMConfig | None
    evaluate: bool = False
    sql: str | None
    status: str = "INVALID"
    completed_at: datetime | None
    tokens_used: int | None
    confidence_score: float | None
    error: str | None
    created_at: datetime = Field(default_factory=datetime.now)
    metadata: dict | None


class NLGeneration(BaseModel):
    id: str | None = None
    sql_generation_id: str
    llm_config: LLMConfig | None
    text: str | None
    created_at: datetime = Field(default_factory=datetime.now)
    metadata: dict | None
