from pydantic import BaseModel

from modules.db_connection.models.entities import DatabaseDialects
from modules.table_description.models.entities import (
    AggrTableDescription,
    SchemaStatus,
    TableDescription,
)
from utils.validation import ObjectIdString


class TableDescriptionResponse(TableDescription):
    metadata: dict | None

    def dict(self, **kwargs):
        dic = super().dict(**kwargs)
        if "metadata" in dic and dic["metadata"] and "dh_internal" in dic["metadata"]:
            del dic["metadata"]["dh_internal"]
        return dic


class ACTableDescriptionResponse(AggrTableDescription):
    pass


class BasicTableDescriptionResponse(BaseModel):
    id: ObjectIdString | None
    name: str | None
    schema_name: str | None
    columns: list[str] | None
    sync_status: SchemaStatus | None
    last_sync: str | None


class DatabaseDescriptionResponse(BaseModel):
    db_connection_id: ObjectIdString
    db_connection_alias: str | None
    dialect: DatabaseDialects | None
    schemas: list[str] | None
    tables: list[BasicTableDescriptionResponse]
