from typing import Any

from modules.db_connection.models.entities import BaseDBConnection


class DBConnectionRequest(BaseDBConnection):
    credential_file_content: dict | str | None = None
    metadata: dict[str, Any] | None = {}
