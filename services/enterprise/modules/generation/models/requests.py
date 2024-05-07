from typing import Any

from pydantic import BaseModel

from modules.generation.models.entities import GenerationStatus, SlackInfo
from utils.validation import ObjectIdString


class SlackInfoRequest(SlackInfo):
    workspace_id: str | None


class SlackGenerationRequest(BaseModel):
    prompt: str
    slack_info: SlackInfoRequest | None


class GenerationUpdateRequest(BaseModel):
    generation_status: GenerationStatus | None
    message: str | None


class SQLRequest(BaseModel):
    sql: str


class PromptRequest(BaseModel):
    text: str
    db_connection_id: ObjectIdString
    metadata: dict[str, Any] | None = {}


class SQLGenerationRequest(BaseModel):
    finetuning_id: ObjectIdString | None
    low_latency_mode: bool | None = False
    evaluate: bool | None = False
    sql: str | None
    metadata: dict[str, Any] | None = {}


class NLGenerationRequest(BaseModel):
    max_rows: int | None
    metadata: dict[str, Any] | None = {}


class PromptSQLGenerationRequest(SQLGenerationRequest):
    prompt: PromptRequest


class SQLNLGenerationRequest(NLGenerationRequest):
    sql_generation: SQLGenerationRequest


class PromptSQLNLGenerationRequest(NLGenerationRequest):
    sql_generation: PromptSQLGenerationRequest


class SQLGenerationExecuteRequest(BaseModel):
    prompt: str
    db_connection_id: ObjectIdString
    finetuning_id: ObjectIdString | None = None
