from datetime import datetime, timezone

from pydantic import BaseModel, validator

from dataherald.db_scanner.models.types import TableDescription
from dataherald.sql_database.models.types import DatabaseConnection


class BaseResponse(BaseModel):
    id: str
    metadata: dict | None
    created_at: str | None

    @validator("created_at", pre=True, always=True)
    def created_at_as_string(cls, v):
        if not v:
            return None
        if isinstance(v, datetime):
            return str(v.replace(tzinfo=timezone.utc))
        if isinstance(v, str):
            return v
        return None


class PromptResponse(BaseResponse):
    text: str
    db_connection_id: str


class SQLGenerationResponse(BaseResponse):
    prompt_id: str
    finetuning_id: str | None
    status: str
    completed_at: str
    sql: str | None
    tokens_used: int | None
    confidence_score: float | None
    error: str | None

    @validator("completed_at", pre=True, always=True)
    def completed_at_as_string(cls, v):
        if not v:
            return None
        if isinstance(v, datetime):
            return str(v.replace(tzinfo=timezone.utc))
        if isinstance(v, str):
            return v
        return None


class NLGenerationResponse(BaseResponse):
    sql_generation_id: str
    text: str | None


class InstructionResponse(BaseResponse):
    instruction: str
    db_connection_id: str


class DatabaseConnectionResponse(DatabaseConnection, BaseResponse):
    pass


class TableDescriptionResponse(TableDescription, BaseResponse):
    pass
