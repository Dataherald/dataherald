from datetime import datetime

import pytz
from pydantic import BaseModel, validator

from dataherald.db_scanner.models.types import TableDescription
from dataherald.sql_database.models.types import DatabaseConnection
from dataherald.types import GoldenSQL, LLMConfig


class BaseResponse(BaseModel):
    id: str
    metadata: dict | None
    created_at: str | None

    @validator("created_at", pre=True, always=True)
    def created_at_as_string(cls, v):
        if not v:
            return None
        if isinstance(v, datetime):
            return str(v.replace(tzinfo=pytz.utc).isoformat())
        return str(v)


class PromptResponse(BaseResponse):
    text: str
    db_connection_id: str


class SQLGenerationResponse(BaseResponse):
    prompt_id: str
    finetuning_id: str | None
    status: str
    completed_at: str | None
    llm_config: LLMConfig | None
    sql: str | None
    tokens_used: int | None
    confidence_score: float | None
    error: str | None

    @validator("completed_at", pre=True, always=True)
    def completed_at_as_string(cls, v):
        if not v:
            return None
        if isinstance(v, datetime):
            return str(v.replace(tzinfo=pytz.utc).isoformat())
        return str(v)


class NLGenerationResponse(BaseResponse):
    llm_config: LLMConfig | None
    sql_generation_id: str
    text: str | None


class InstructionResponse(BaseResponse):
    instruction: str
    db_connection_id: str


class DatabaseConnectionResponse(BaseResponse, DatabaseConnection):
    pass


class TableDescriptionResponse(BaseResponse, TableDescription):
    id: str | None


class GoldenSQLResponse(BaseResponse, GoldenSQL):
    pass
