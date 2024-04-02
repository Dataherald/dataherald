from datetime import datetime

from pydantic import BaseModel

from modules.generation.models.entities import (
    BaseNLGeneration,
    BasePrompt,
    BaseSQLGeneration,
    Generation,
    GenerationSource,
    GenerationStatus,
)
from utils.validation import ObjectIdString


class GenerationSlackResponse(BaseModel):
    id: ObjectIdString
    display_id: str
    nl_generation_text: str | None
    sql: str
    exec_time: float | None = None
    is_above_confidence_threshold: bool = False


class GenerationListResponse(BaseModel):
    id: ObjectIdString
    created_by: str
    prompt_text: str
    db_connection_alias: str | None
    nl_generation_text: str | None
    sql: str | None
    status: GenerationStatus | None
    confidence_score: float | None
    source: GenerationSource | None
    display_id: str | None
    created_at: datetime | None
    slack_message_last_sent_at: datetime | None


class GenerationResponse(Generation):
    pass


class PromptResponse(BasePrompt):
    metadata: dict | None

    def dict(self, **kwargs):
        dic = super().dict(**kwargs)
        if "metadata" in dic and dic["metadata"] and "dh_internal" in dic["metadata"]:
            del dic["metadata"]["dh_internal"]
        return dic


class SQLGenerationResponse(BaseSQLGeneration):
    metadata: dict | None

    def dict(self, **kwargs):
        dic = super().dict(**kwargs)
        if "metadata" in dic and dic["metadata"] and "dh_internal" in dic["metadata"]:
            del dic["metadata"]["dh_internal"]
        return dic


class NLGenerationResponse(BaseNLGeneration):
    metadata: dict | None

    def dict(self, **kwargs):
        dic = super().dict(**kwargs)
        if "metadata" in dic and dic["metadata"] and "dh_internal" in dic["metadata"]:
            del dic["metadata"]["dh_internal"]
        return dic
