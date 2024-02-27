from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)

from exceptions.error_codes import BaseErrorCode, ErrorCodeData
from exceptions.exceptions import BaseError


class GoldenSQLErrorCode(BaseErrorCode):
    golden_sql_not_found = ErrorCodeData(
        status_code=HTTP_404_NOT_FOUND, message="Golden SQL not found"
    )
    cannot_delete_golden_sql = ErrorCodeData(
        status_code=HTTP_400_BAD_REQUEST, message="Cannot delete golden SQL"
    )


class GoldenSQLError(BaseError):
    """
    Base class for golden SQL exceptions
    """

    ERROR_CODES: BaseErrorCode = GoldenSQLErrorCode


class GoldenSqlNotFoundError(GoldenSQLError):
    def __init__(self, golden_sql_id: str, org_id: str) -> None:
        super().__init__(
            error_code=GoldenSQLErrorCode.golden_sql_not_found.name,
            detail={"golden_sql_id": golden_sql_id, "organization_id": org_id},
        )


class CannotDeleteGoldenSqlError(GoldenSQLError):
    def __init__(self, golden_sql_id: str, org_id: str) -> None:
        super().__init__(
            error_code=GoldenSQLErrorCode.cannot_delete_golden_sql.name,
            detail={"golden_sql_id": golden_sql_id, "organization_id": org_id},
        )
