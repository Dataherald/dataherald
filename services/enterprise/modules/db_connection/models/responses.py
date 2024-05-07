from pydantic import BaseModel

from modules.db_connection.models.entities import DatabaseDialects, DBConnection
from utils.validation import ObjectIdString


class DBConnectionResponse(DBConnection):
    metadata: dict | None

    def dict(self, **kwargs):
        dic = super().dict(**kwargs)
        if "metadata" in dic and dic["metadata"] and "dh_internal" in dic["metadata"]:
            del dic["metadata"]["dh_internal"]
        return dic


class SampleDBConnectionResponse(BaseModel):
    id: ObjectIdString | None
    alias: str | None
    dialect: DatabaseDialects | None
    description: str | None
    example_prompts: list[str] | None
