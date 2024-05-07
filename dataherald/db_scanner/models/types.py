from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, validator


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
    NOT_SCANNED = "NOT_SCANNED"
    SYNCHRONIZING = "SYNCHRONIZING"
    DEPRECATED = "DEPRECATED"
    SCANNED = "SCANNED"
    FAILED = "FAILED"


class TableDescription(BaseModel):
    id: str | None
    db_connection_id: str
    schema_name: str | None
    table_name: str
    description: str | None
    table_schema: str | None
    columns: list[ColumnDetail] = []
    examples: list = []
    last_schema_sync: datetime | None
    status: str = TableDescriptionStatus.SCANNED.value
    error_message: str | None
    metadata: dict | None
    created_at: datetime = Field(default_factory=datetime.now)

    @validator("last_schema_sync", pre=True)
    def parse_datetime_with_timezone(cls, value):
        if not value:
            return None
        return value.replace(tzinfo=timezone.utc)  # Set the timezone to UTC


class QueryHistory(BaseModel):
    id: str | None
    db_connection_id: str
    table_name: str
    query: str
    user: str
    occurrences: int = 0
