from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Extra

from utils.validation import ObjectIdString


class FineTuningStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    VALIDATING_FILES = "validating_files"


class BaseLLM(BaseModel):
    model_name: str
    model_provider: str | None
    model_parameters: dict[str, str] | None


class DHFinetuningMetadata(BaseModel):
    organization_id: ObjectIdString | None


class FinetuningMetadata(BaseModel):
    dh_internal: DHFinetuningMetadata | None

    class Config:
        extra = Extra.allow


class BaseFinetuning(BaseModel):
    id: ObjectIdString
    alias: str
    db_connection_id: str
    status: str = FineTuningStatus.QUEUED
    error: str | None
    base_llm: BaseLLM | None
    schemas: list[str] | None
    finetuning_file_id: str | None
    finetuning_job_id: str | None
    model_id: str | None
    created_at: datetime | None
    golden_sqls: list[str] | None
    metadata: FinetuningMetadata | None


class Finetuning(BaseFinetuning):
    pass


class AggrFinetuning(Finetuning):
    db_connection_alias: str | None
