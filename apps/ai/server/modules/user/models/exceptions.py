from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT

from exceptions.error_codes import BaseErrorCode, ErrorCodeData
from exceptions.exceptions import BaseError


class UserErrorCode(BaseErrorCode):
    user_not_found = ErrorCodeData(
        status_code=HTTP_404_NOT_FOUND, message="User not found"
    )
    user_exists_in_org = ErrorCodeData(
        status_code=HTTP_409_CONFLICT,
        message="User already exists in organization",
    )
    user_exists_in_other_org = ErrorCodeData(
        status_code=HTTP_409_CONFLICT,
        message="User already exists in other organization",
    )
    cannot_create_user = ErrorCodeData(
        status_code=HTTP_400_BAD_REQUEST, message="Cannot create user"
    )
    cannot_update_user = ErrorCodeData(
        status_code=HTTP_400_BAD_REQUEST, message="Cannot update user"
    )
    cannot_delete_user = ErrorCodeData(
        status_code=HTTP_400_BAD_REQUEST, message="Cannot delete user"
    )
    cannot_delete_last_user = ErrorCodeData(
        status_code=HTTP_400_BAD_REQUEST, message="Cannot delete last user"
    )


class UserError(BaseError):
    """
    Base class for user exceptions
    """

    ERROR_CODES: BaseErrorCode = UserErrorCode


class UserNotFoundError(UserError):
    def __init__(self, user_id: str, org_id: str) -> None:
        super().__init__(
            error_code=UserErrorCode.user_not_found.name,
            detail={"user_id": user_id, "organization_id": org_id},
        )


class UserExistsInOrgError(UserError):
    def __init__(self, user_id: str, org_id: str) -> None:
        super().__init__(
            error_code=UserErrorCode.user_exists_in_org.name,
            detail={"user_id": user_id, "organization_id": org_id},
        )


class UserExistsInOtherOrgError(UserError):
    def __init__(self, user_id: str, org_id: str) -> None:
        super().__init__(
            error_code=UserErrorCode.user_exists_in_other_org.name,
            detail={"user_id": user_id, "organization_id": org_id},
        )


class CannotCreateUserError(UserError):
    def __init__(self, org_id: str) -> None:
        super().__init__(
            error_code=UserErrorCode.cannot_create_user.name,
            detail={"organization_id": org_id},
        )


class CannotUpdateUserError(UserError):
    def __init__(self, user_id: str, org_id: str) -> None:
        super().__init__(
            error_code=UserErrorCode.cannot_update_user.name,
            detail={"user_id": user_id, "organization_id": org_id},
        )


class CannotDeleteUserError(UserError):
    def __init__(self, user_id: str, org_id: str) -> None:
        super().__init__(
            error_code=UserErrorCode.cannot_delete_user.name,
            detail={"user_id": user_id, "organization_id": org_id},
        )


class CannotDeleteLastUserError(UserError):
    def __init__(self, user_id: str, org_id: str) -> None:
        super().__init__(
            error_code=UserErrorCode.cannot_delete_last_user.name,
            detail={"user_id": user_id, "organization_id": org_id},
        )
