from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)

from exceptions.error_codes import BaseErrorCode, ErrorCodeData
from exceptions.exceptions import BaseError


class DBConnectionErrorCode(BaseErrorCode):
    db_connection_not_found = ErrorCodeData(
        status_code=HTTP_404_NOT_FOUND, message="Database connection not found"
    )
    db_connection_alias_exists = ErrorCodeData(
        status_code=HTTP_400_BAD_REQUEST,
        message="Existing database connection already has alias",
    )


class DBConnectionError(BaseError):
    """
    Base class for database connection exceptions
    """

    ERROR_CODES: BaseErrorCode = DBConnectionErrorCode


class DBConnectionNotFoundError(DBConnectionError):
    def __init__(self, db_connection_id: str, org_id: str) -> None:
        super().__init__(
            error_code=DBConnectionErrorCode.db_connection_not_found.name,
            detail={
                "db_connection_id": db_connection_id,
                "organization_id": org_id,
            },
        )


class DBConnectionAliasExistsError(DBConnectionError):
    def __init__(self, db_connection_id: str, org_id: str) -> None:
        super().__init__(
            error_code=DBConnectionErrorCode.db_connection_alias_exists.name,
            detail={"db_connection_id": db_connection_id, "organization_id": org_id},
        )
