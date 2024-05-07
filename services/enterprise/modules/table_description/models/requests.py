from typing import Any

from pydantic import BaseModel

from modules.table_description.models.entities import ColumnDescription
from utils.validation import ObjectIdString


class TableDescriptionRequest(BaseModel):
    description: str | None
    columns: list[ColumnDescription] | None
    examples: list | None
    metadata: dict[str, Any] | None = {}


class ScanRequest(BaseModel):
    ids: list[ObjectIdString]
    metadata: dict[str, Any] | None = {}
