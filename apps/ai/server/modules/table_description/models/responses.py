from pydantic import BaseModel

from modules.table_description.models.entities import SchemaStatus, TableDescription


class TableDescriptionResponse(TableDescription):
    pass


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
