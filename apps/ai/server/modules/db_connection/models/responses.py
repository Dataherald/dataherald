from modules.db_connection.models.entities import (
    BaseDBConnection,
    Driver,
    LLMCredentials,
)


class DBConnectionResponse(BaseDBConnection):
    id: str
    uri: str | None
    llm_credentials: LLMCredentials | None


class DriverResponse(Driver):
    pass
