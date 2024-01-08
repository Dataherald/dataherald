from datetime import datetime

from pydantic import BaseModel

from modules.generation.models.entities import (
    BaseNLGeneration,
    BasePrompt,
    BaseSQLGeneration,
    Generation,
    GenerationStatus,
)


class GenerationSlackResponse(BaseModel):
    id: str
    display_id: str
    nl_generation_text: str | None
    sql: str
    exec_time: float | None = None
    is_above_confidence_threshold: bool = False


class GenerationListResponse(BaseModel):
    id: str
    created_by: str
    prompt_text: str
    nl_generation_text: str | None
    sql: str | None
    status: GenerationStatus | None
    confidence_score: float | None
    display_id: str | None
    created_at: datetime | None


class GenerationResponse(Generation):
    pass


class PromptResponse(BasePrompt):
    def dict(self, **kwargs):
        dic = super().dict(**kwargs)
        if "metadata" in dic and dic["metadata"] and "dh_internal" in dic["metadata"]:
            del dic["metadata"]["dh_internal"]
        return dic


class SQLGenerationResponse(BaseSQLGeneration):
    def dict(self, **kwargs):
        dic = super().dict(**kwargs)
        if "metadata" in dic and dic["metadata"] and "dh_internal" in dic["metadata"]:
            del dic["metadata"]["dh_internal"]
        return dic


class NLGenerationResponse(BaseNLGeneration):
    def dict(self, **kwargs):
        dic = super().dict(**kwargs)
        if "metadata" in dic and dic["metadata"] and "dh_internal" in dic["metadata"]:
            del dic["metadata"]["dh_internal"]
        return dic
