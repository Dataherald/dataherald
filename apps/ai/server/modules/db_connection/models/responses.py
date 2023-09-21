from modules.db_connection.models.entities import BaseDBConnection, Driver


class DBConnectionResponse(BaseDBConnection):
    id: str
    uri: str


class DriverResponse(Driver):
    pass
