from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class SchemaStatus(Enum):
    NOT_SYNCHRONIZED = "NOT_SYNCHRONIZED"
    SYNCHRONIZING = "SYNCHRONIZING"
    SYNCHRONIZED = "SYNCHRONIZED"
    DEPRECATED = "DEPRECATED"
    FAILED = "FAILED"


class ColumnDescription(BaseModel):
    name: str | None
    description: str | None
    is_primary_key: bool | None
    data_type: str | None
    low_cardinality: bool | None
    categories: list[str] | None
    forengin_key: dict | None


class BaseTableDescription(BaseModel):
    description: str | None
    columns: list[ColumnDescription] | None
    examples: list | None


class TableDescription(BaseTableDescription):
    id: Any = Field(alias="_id")
    table_name: str | None
