from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)

from exceptions.error_codes import BaseErrorCode, ErrorCodeData
from exceptions.exceptions import BaseError


class FinetuningErrorCode(BaseErrorCode):
    finetuning_not_found = ErrorCodeData(
        status_code=HTTP_404_NOT_FOUND, message="Finetuning not found"
    )
    finetuning_alias_exists = ErrorCodeData(
        status_code=HTTP_400_BAD_REQUEST,
        message="Existing finetuning already has alias",
    )


class FinetuningError(BaseError):
    """
    Base class for finetuning exceptions
    """

    ERROR_CODES: BaseErrorCode = FinetuningErrorCode


class FinetuningNotFoundError(FinetuningError):
    def __init__(self, finetuning_id: str, org_id: str) -> None:
        super().__init__(
            error_code=FinetuningErrorCode.finetuning_not_found.name,
            detail={"finetuning_id": finetuning_id, "organization_id": org_id},
        )


class FinetuningAliasExistsError(FinetuningError):
    def __init__(self, finetuning_id: str, org_id: str) -> None:
        super().__init__(
            error_code=FinetuningErrorCode.finetuning_alias_exists.name,
            detail={"finetuning_id": finetuning_id, "organization_id": org_id},
        )
