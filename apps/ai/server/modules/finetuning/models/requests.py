from typing import Any

from pydantic import BaseModel

from modules.finetuning.models.entities import BaseLLM
from utils.validation import ObjectIdString


class FinetuningRequest(BaseModel):
    db_connection_id: ObjectIdString
    alias: str
    base_llm: BaseLLM
    schemas: list[str] | None
    golden_sqls: list[str] = []
    metadata: dict[str, Any] | None = {}
