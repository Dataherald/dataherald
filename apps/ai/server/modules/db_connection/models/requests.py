from modules.db_connection.models.entities import BaseDBConnection


class DBConnectionRequest(BaseDBConnection):
    connection_uri: str | None
    pass
