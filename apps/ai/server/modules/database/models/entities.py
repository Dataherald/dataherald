from typing import Any

from pydantic import BaseModel, Field

from modules.database.models.requests import DatabaseConnectionRequest


class DatabaseConnection(DatabaseConnectionRequest):
    id: Any = Field(alias="_id")


class DatabaseConnectionRef(BaseModel):
    id: Any = Field(alias="_id")
    db_connection_id: Any
    organization_id: Any
    db_alias: str
