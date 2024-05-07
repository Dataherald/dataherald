from starlette.status import (
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from exceptions.error_codes import BaseErrorCode, ErrorCodeData
from exceptions.exceptions import BaseError


class AuthErrorCode(BaseErrorCode):
    unauthorized_user = ErrorCodeData(
        status_code=HTTP_401_UNAUTHORIZED, message="Unauthorized user"
    )
    unauthorized_operation = ErrorCodeData(
        status_code=HTTP_401_UNAUTHORIZED, message="Unauthorized operation"
    )
    unauthorized_data_access = ErrorCodeData(
        status_code=HTTP_401_UNAUTHORIZED, message="Unauthorized data access"
    )
    bearer_token_expired = ErrorCodeData(
        status_code=HTTP_401_UNAUTHORIZED, message="Bearer token expired"
    )
    invalid_bearer_token = ErrorCodeData(
        status_code=HTTP_403_FORBIDDEN, message="Bearer token is invalid"
    )
    invalid_or_revoked_key = ErrorCodeData(
        status_code=HTTP_403_FORBIDDEN, message="Invalid or revoked API key"
    )
    py_jwk_client_error = ErrorCodeData(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR, message="PyJWKClient error"
    )
    decode_error = ErrorCodeData(
        status_code=HTTP_401_UNAUTHORIZED, message="Decode error"
    )


class AuthError(BaseError):
    """
    Base class for auth exceptions
    """

    ERROR_CODES: BaseErrorCode = AuthErrorCode


class UnauthorizedUserError(AuthError):
    def __init__(self, email: str) -> None:
        super().__init__(
            error_code=AuthErrorCode.unauthorized_user.name,
            detail={"email": email},
        )


class UnauthorizedOperationError(AuthError):
    def __init__(self, user_id: str) -> None:
        super().__init__(
            error_code=AuthErrorCode.unauthorized_operation.name,
            detail={"user_id": user_id},
        )


class UnauthorizedDataAccessError(AuthError):
    def __init__(self, user_id: str) -> None:
        super().__init__(
            error_code=AuthErrorCode.unauthorized_data_access.name,
            detail={"user_id": user_id},
        )


class InvalidOrRevokedAPIKeyError(AuthError):
    def __init__(self, key_id: str) -> None:
        super().__init__(
            error_code=AuthErrorCode.invalid_or_revoked_key.name,
            detail={"key_id": key_id},
        )


class BearerTokenExpiredError(AuthError):
    def __init__(self) -> None:
        super().__init__(error_code=AuthErrorCode.bearer_token_expired.name)


class InvalidBearerTokenError(AuthError):
    def __init__(self) -> None:
        super().__init__(error_code=AuthErrorCode.invalid_bearer_token.name)


class PyJWKClientError(AuthError):
    def __init__(self) -> None:
        super().__init__(error_code=AuthErrorCode.py_jwk_client_error.name)


class DecodeError(AuthError):
    def __init__(self) -> None:
        super().__init__(error_code=AuthErrorCode.decode_error.name)
