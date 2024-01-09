from datetime import datetime

from pydantic import BaseModel

from dataherald.db_scanner.models.types import TableDescription
from dataherald.sql_database.models.types import DatabaseConnection


class BaseResponse(BaseModel):
    id: str
    metadata: dict | None
    created_at: datetime | None


class PromptResponse(BaseResponse):
    text: str
    db_connection_id: str


class SQLGenerationResponse(BaseResponse):
    prompt_id: str
    finetuning_id: str | None
    status: str
    completed_at: datetime | None
    sql: str | None
    tokens_used: int | None
    confidence_score: float | None
    error: str | None


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
