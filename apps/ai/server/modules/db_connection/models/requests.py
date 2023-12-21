from typing import Any

from modules.db_connection.models.entities import BaseDBConnection


class DBConnectionRequest(BaseDBConnection):
    metadata: dict[str, Any] | None = {}
