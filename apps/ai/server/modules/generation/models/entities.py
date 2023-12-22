from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Extra, confloat

from modules.user.models.entities import SlackInfo


class GenerationStatus(str, Enum):
    INITIALIZED = "INITIALIZED"
    IN_PROGRESS = "IN_PROGRESS"
    NOT_VERIFIED = "NOT_VERIFIED"
    VERIFIED = "VERIFIED"
    ERROR = "ERROR"
    REJECTED = "REJECTED"


class DHPromptMetadata(BaseModel):
    generation_status: GenerationStatus | None
    created_by: str | None
    updated_by: str | None
    organization_id: str | None
    display_id: str | None
    slack_info: SlackInfo | None
    message: str | None


class PromptMetadata(BaseModel):
    dh_internal: DHPromptMetadata | None

    class Config:
        extra = Extra.allow


class SQLGenerationStatus(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"


class BasePrompt(BaseModel):
    id: str
    text: str
    db_connection_id: str
    metadata: PromptMetadata | None
    created_at: datetime | None


class Prompt(BasePrompt):
    pass


class DHSQLGenerationMetadata(BaseModel):
    organization_id: str | None


class SQLGenerationMetadata(BaseModel):
    dh_internal: DHSQLGenerationMetadata | None

    class Config:
        extra = Extra.allow


class BaseSQLGeneration(BaseModel):
    id: str | None
    prompt_id: str | None
    finetuning_id: str | None
    sql: str | None
    status: SQLGenerationStatus = SQLGenerationStatus.INVALID
    tokens_used: int | None
    confidence_score: confloat(ge=0, le=1) | None
    error: str | None
    completed_at: datetime | None
    created_at: datetime | None
    metadata: SQLGenerationMetadata | None


class SQLGeneration(BaseSQLGeneration):
    pass


class DHNLGenerationMetadata(BaseModel):
    organization_id: str | None


class NLGenerationMetadata(BaseModel):
    dh_internal: DHNLGenerationMetadata | None

    class Config:
        extra = Extra.allow


class BaseNLGeneration(BaseModel):
    id: str | None
    text: str | None
    sql_generation_id: str | None
    metadata: NLGenerationMetadata | None
    created_at: datetime | None


class NLGeneration(BaseNLGeneration):
    pass


class Generation(BaseModel):
    # Prompt
    id: str
    db_connection_id: str
    prompt_text: str
    created_by: str | None
    updated_by: str | None
    organization_id: str | None
    display_id: str | None
    slack_info: SlackInfo | None
    message: str | None
    # SQLGeneration
    sql: str | None
    confidence_score: float | None
    sql_generation_error: str | None
    # NLGeneration
    nl_generation_text: str | None

    updated_at: datetime | None
    created_at: datetime | None
    status: GenerationStatus | None  # inferred from SQLGeneration and NLGeneration
    sql_results: dict | None
