from typing import Any

from pydantic import BaseModel

from modules.generation.models.entities import GenerationStatus, SlackInfo


class SlackInfoRequest(SlackInfo):
    workspace_id: str | None


class SlackGenerationRequest(BaseModel):
    prompt: str
    slack_info: SlackInfoRequest | None


class GenerationUpdateRequest(BaseModel):
    generation_status: GenerationStatus | None
    message: str | None


class SQLRequest(BaseModel):
    sql: str | None


class PromptRequest(BaseModel):
    text: str
    db_connection_id: str
    metadata: dict[str, Any] | None = {}


class SQLGenerationRequest(BaseModel):
    finetuning_id: str | None
    evaluate: bool | None
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
    model: str | None = None
