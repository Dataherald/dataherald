from pydantic import BaseModel, Extra

from modules.table_description.models.entities import BaseTableDescription, SchemaStatus


class TableDescriptionResponse(BaseTableDescription):
    id: str | None
    table_name: str
    status: SchemaStatus | None
    last_schema_sync: str | None

    class Config:
        extra = Extra.ignore


class BasicTableDescriptionResponse(BaseModel):
    id: str | None
    name: str | None
    columns: list[str] | None
    sync_status: SchemaStatus | None
    last_sync: str | None


class DatabaseDescriptionResponse(BaseModel):
    alias: str
    tables: list[BasicTableDescriptionResponse]
    db_connection_id: str | None
