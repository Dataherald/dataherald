from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel


class ForeignKeyDetail(BaseModel):
    field_name: str
    reference_table: str


class ColumnDetail(BaseModel):
    name: str
    is_primary_key: bool = False
    data_type: str = "str"
    description: str | None
    low_cardinality: bool = False
    categories: list[Any] | None
    foreign_key: ForeignKeyDetail | None


class TableDescriptionStatus(Enum):
    NOT_SYNCHRONIZED = "NOT_SYNCHRONIZED"
    SYNCHRONIZING = "SYNCHRONIZING"
    DEPRECATED = "DEPRECATED"
    SYNCHRONIZED = "SYNCHRONIZED"
    FAILED = "FAILED"


class TableSchemaDetail(BaseModel):
    id: Any
    db_connection_id: str
    table_name: str
    description: str | None
    table_schema: str | None
    columns: list[ColumnDetail] = []
    examples: list = []
    last_schema_sync: datetime | None
    status: str = TableDescriptionStatus.SYNCHRONIZED.value
    error_message: str | None
