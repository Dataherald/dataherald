from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Extra, confloat

from utils.validation import ObjectIdString


class GenerationStatus(str, Enum):
    INITIALIZED = "INITIALIZED"
    IN_PROGRESS = "IN_PROGRESS"
    NOT_VERIFIED = "NOT_VERIFIED"
    VERIFIED = "VERIFIED"
    ERROR = "ERROR"
    REJECTED = "REJECTED"


class GenerationSource(str, Enum):
    API = "API"
    SLACK = "SLACK"
    PLAYGROUND = "PLAYGROUND"
    QUERY_EDITOR_RUN = "QUERY_EDITOR_RUN"
    QUERY_EDITOR_RESUBMIT = "QUERY_EDITOR_RESUBMIT"


class SlackInfo(BaseModel):
    user_id: str | None
    channel_id: str | None
    thread_ts: str | None


class DHPromptMetadata(BaseModel):
    generation_status: GenerationStatus | None
    created_by: str | None
    updated_by: str | None
    organization_id: ObjectIdString | None
    display_id: str | None
    message: str | None
    source: GenerationSource | None
    slack_info: SlackInfo | None
    slack_message_last_sent_at: datetime | None


class PromptMetadata(BaseModel):
    dh_internal: DHPromptMetadata | None

    class Config:
        extra = Extra.allow


class SQLGenerationStatus(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"


class BasePrompt(BaseModel):
    id: ObjectIdString | None
    text: str
    db_connection_id: ObjectIdString
    metadata: PromptMetadata | None
    created_at: datetime | None


class Prompt(BasePrompt):
    pass


class DHSQLGenerationMetadata(BaseModel):
    organization_id: ObjectIdString | None


class SQLGenerationMetadata(BaseModel):
    dh_internal: DHSQLGenerationMetadata | None

    class Config:
        extra = Extra.allow


class BaseSQLGeneration(BaseModel):
    id: ObjectIdString | None
    prompt_id: str | None
    finetuning_id: ObjectIdString | None
    sql: str | None
    status: SQLGenerationStatus = SQLGenerationStatus.INVALID
    confidence_score: confloat(ge=0, le=1) | None
    error: str | None
    completed_at: datetime | None
    created_at: datetime | None
    metadata: SQLGenerationMetadata | None


class SQLGeneration(BaseSQLGeneration):
    pass


class DHNLGenerationMetadata(BaseModel):
    organization_id: ObjectIdString | None


class NLGenerationMetadata(BaseModel):
    dh_internal: DHNLGenerationMetadata | None

    class Config:
        extra = Extra.allow


class BaseNLGeneration(BaseModel):
    id: ObjectIdString | None
    text: str | None
    sql_generation_id: ObjectIdString | None
    metadata: NLGenerationMetadata | None
    created_at: datetime | None


class NLGeneration(BaseNLGeneration):
    pass


class Generation(BaseModel):
    # db connection
    db_connection_id: ObjectIdString
    db_connection_alias: str | None
    # Prompt
    id: ObjectIdString
    prompt_text: str
    created_by: str | None
    updated_by: str | None
    organization_id: ObjectIdString | None
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
    status: GenerationStatus | None
    source: GenerationSource | None
    sql_result: dict | None
    slack_message_last_sent_at: datetime | None


class SQLGenerationAggregation(SQLGeneration):
    nl_generation: NLGeneration | None


class PromptAggregation(Prompt):
    sql_generation: SQLGenerationAggregation | None
