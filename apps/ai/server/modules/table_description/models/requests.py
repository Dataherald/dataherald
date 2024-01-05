from typing import Any

from pydantic import BaseModel

from modules.table_description.models.entities import ColumnDescription


class TableDescriptionRequest(BaseModel):
    description: str | None
    columns: list[ColumnDescription] | None
    examples: list | None
    metadata: dict[str, Any] | None = {}


class ScanRequest(BaseModel):
    db_connection_id: str
    table_names: list[str] | None
    metadata: dict[str, Any] | None = {}
