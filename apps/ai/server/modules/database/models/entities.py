from typing import Any

from pydantic import Field

from modules.database.models.requests import DatabaseConnectionRequest


class DatabaseConnection(DatabaseConnectionRequest):
    id: Any = Field(alias="_id")
