from starlette.status import (
    HTTP_404_NOT_FOUND,
)

from exceptions.error_codes import BaseErrorCode, ErrorCodeData
from exceptions.exceptions import BaseError


class TableDescriptionErrorCode(BaseErrorCode):
    table_description_not_found = ErrorCodeData(
        status_code=HTTP_404_NOT_FOUND, message="Table description not found"
    )


class TableDescriptionError(BaseError):
    """
    Base class for table description exceptions
    """

    ERROR_CODES: BaseErrorCode = TableDescriptionErrorCode


class TableDescriptionNotFoundError(TableDescriptionError):
    def __init__(self, table_description_id: str, org_id: str) -> None:
        super().__init__(
            error_code=TableDescriptionErrorCode.table_description_not_found.name,
            detail={
                "table_description_id": table_description_id,
                "organization_id": org_id,
            },
        )
