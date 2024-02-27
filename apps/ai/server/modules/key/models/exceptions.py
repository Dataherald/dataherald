from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
)

from exceptions.error_codes import BaseErrorCode, ErrorCodeData
from exceptions.exceptions import BaseError


class KeyErrorCode(BaseErrorCode):
    key_not_found = ErrorCodeData(
        status_code=HTTP_401_UNAUTHORIZED, message="API key not found"
    )
    key_name_exists = ErrorCodeData(
        status_code=HTTP_400_BAD_REQUEST, message="Existing key already has name"
    )
    cannot_revoke_key = ErrorCodeData(
        status_code=HTTP_400_BAD_REQUEST, message="Cannot revoke api key"
    )
    cannot_create_key = ErrorCodeData(
        status_code=HTTP_400_BAD_REQUEST, message="Cannot create api key"
    )


class KeyError(BaseError):
    """
    Base class for  api key exceptions
    """

    ERROR_CODES: BaseErrorCode = KeyErrorCode


class KeyNotFoundError(KeyError):
    def __init__(self, key_id: str, org_id: str) -> None:
        super().__init__(
            error_code=KeyErrorCode.key_not_found.name,
            detail={"key_id": key_id, "organization_id": org_id},
        )


class KeyNameExistsError(KeyError):
    def __init__(self, key_id: str, org_id: str) -> None:
        super().__init__(
            error_code=KeyErrorCode.key_name_exists.name,
            detail={"key_id": key_id, "organization_id": org_id},
        )


class CannotRevokeKeyError(KeyError):
    def __init__(self, key_id: str, org_id: str) -> None:
        super().__init__(
            error_code=KeyErrorCode.cannot_revoke_key.name,
            detail={"key_id": key_id, "organization_id": org_id},
        )


class CannotCreateKeyError(KeyError):
    def __init__(self, org_id: str) -> None:
        super().__init__(
            error_code=KeyErrorCode.cannot_create_key.name,
            detail={"organization_id": org_id},
        )
