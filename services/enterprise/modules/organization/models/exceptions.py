from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)

from exceptions.error_codes import BaseErrorCode, ErrorCodeData
from exceptions.exceptions import BaseError


class OrganizationErrorCode(BaseErrorCode):
    organization_not_found = ErrorCodeData(
        status_code=HTTP_404_NOT_FOUND, message="Organization not found"
    )
    slack_installation_not_found = ErrorCodeData(
        status_code=HTTP_404_NOT_FOUND, message="Slack installation not found"
    )
    cannot_create_organization = ErrorCodeData(
        status_code=HTTP_400_BAD_REQUEST, message="Cannot create organization"
    )
    cannot_update_organization = ErrorCodeData(
        status_code=HTTP_400_BAD_REQUEST, message="Cannot update organization"
    )
    cannot_delete_organization = ErrorCodeData(
        status_code=HTTP_400_BAD_REQUEST, message="Cannot delete organization"
    )
    invalid_llm_api_key = ErrorCodeData(
        status_code=HTTP_400_BAD_REQUEST, message="Invalid LLM API key"
    )


class OrganizationError(BaseError):
    """
    Base class for organization exceptions
    """

    ERROR_CODES: BaseErrorCode = OrganizationErrorCode


class OrganizationNotFoundError(OrganizationError):
    def __init__(
        self, slack_workspace_id: str | None, organization_id: str | None
    ) -> None:
        if slack_workspace_id:
            detail = {"slack_workspace_id": slack_workspace_id}
        elif organization_id:
            detail = {"organization_id": organization_id}
        else:
            raise ValueError("workspace_id or organization_id must be provided")
        super().__init__(
            error_code=OrganizationErrorCode.organization_not_found.name,
            detail=detail,
        )


class SlackInstallationNotFoundError(OrganizationError):
    def __init__(self, slack_workspace_id: str) -> None:
        super().__init__(
            error_code=OrganizationErrorCode.slack_installation_not_found.name,
            detail={"slack_workspace_id": slack_workspace_id},
        )


class CannotCreateOrganizationError(OrganizationError):
    def __init__(self) -> None:
        super().__init__(
            error_code=OrganizationErrorCode.cannot_create_organization.name,
        )


class CannotUpdateOrganizationError(OrganizationError):
    def __init__(self, organization_id: str) -> None:
        super().__init__(
            error_code=OrganizationErrorCode.cannot_update_organization.name,
            detail={"organization_id": organization_id},
        )


class CannotDeleteOrganizationError(OrganizationError):
    def __init__(self, organization_id: str) -> None:
        super().__init__(
            error_code=OrganizationErrorCode.cannot_delete_organization.name,
            detail={"organization_id": organization_id},
        )


class InvalidLlmApiKeyError(OrganizationError):
    def __init__(self) -> None:
        super().__init__(
            error_code=OrganizationErrorCode.invalid_llm_api_key.name,
        )
