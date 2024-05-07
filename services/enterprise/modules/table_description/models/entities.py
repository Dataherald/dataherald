from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Extra

from utils.validation import ObjectIdString


class SchemaStatus(str, Enum):
    NOT_SCANNED = "NOT_SCANNED"
    SYNCHRONIZING = "SYNCHRONIZING"
    SCANNED = "SCANNED"
    DEPRECATED = "DEPRECATED"
    FAILED = "FAILED"


class ColumnDescription(BaseModel):
    name: str | None
    description: str | None
    is_primary_key: bool | None
    data_type: str | None
    low_cardinality: bool | None
    categories: list[str] | None
    foreign_key: dict | None


class DHTableDescriptionMetadata(BaseModel):
    organization_id: ObjectIdString | None


class TableDescriptionMetadata(BaseModel):
    dh_internal: DHTableDescriptionMetadata | None

    class Config:
        extra = Extra.allow


class BaseTableDescription(BaseModel):
    id: ObjectIdString | None
    table_name: str | None
    db_connection_id: ObjectIdString
    description: str | None
    schema_name: str | None
    columns: list[ColumnDescription] | None
    table_schema: str | None
    examples: list | None
    status: SchemaStatus | None
    last_schema_sync: datetime | None
    created_at: datetime | None

    class Config:
        extra = Extra.ignore


class TableDescription(BaseTableDescription):
    metadata: TableDescriptionMetadata | None


class AggrTableDescription(TableDescription):
    db_connection_alias: str | None
