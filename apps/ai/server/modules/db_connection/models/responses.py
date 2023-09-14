from pydantic import Field

from modules.db_connection.models.entities import BaseDBConnection


class DBConnectionResponse(BaseDBConnection):
    id: str = Field(alias="_id")
