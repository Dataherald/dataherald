from fastapi import APIRouter, Security, status

from modules.organization.models.entities import SlackInstallation
from modules.organization.models.requests import (
    OrganizationRequest,
    SlackInstallationRequest,
)
from modules.organization.models.responses import OrganizationResponse
from modules.organization.service import OrganizationService
from utils.auth import Authorize, User, authenticate_user, verify_token
from utils.validation import ObjectIdString

router = APIRouter(
    prefix="/organizations",
    responses={404: {"description": "Not found"}},
)

authorize = Authorize()
org_service = OrganizationService()


@router.get("")
async def get_organizations(
    user: User = Security(authenticate_user),
) -> list[OrganizationResponse]:
    authorize.is_admin_user(user)
    return org_service.get_organizations()


@router.get("/{id}")
async def get_organization(
    id: ObjectIdString, user: User = Security(authenticate_user)
) -> OrganizationResponse:
    authorize.user_in_organization(user.id, id)
    return org_service.get_organization(id)


@router.post("", status_code=status.HTTP_201_CREATED)
async def add_organization(
    org_request: OrganizationRequest, user: User = Security(authenticate_user)
) -> OrganizationResponse:
    authorize.is_admin_user(user)
    return org_service.add_organization(
        OrganizationRequest(**org_request.dict(exclude={"owner"}), owner=user.id)
    )


@router.put("/{id}")
async def update_organization(
    id: ObjectIdString,
    org_request: OrganizationRequest,
    user: User = Security(authenticate_user),
) -> OrganizationResponse:
    authorize.user_in_organization(user.id, id)
    return org_service.update_organization(id, org_request)


@router.delete("/{id}")
async def delete_organization(
    id: ObjectIdString, user: User = Security(authenticate_user)
):
    authorize.is_admin_user(user)
    authorize.is_not_self(user.organization_id, id)
    return org_service.delete_organization(id)


@router.post("/slack/installation", status_code=status.HTTP_201_CREATED)
async def add_organization_by_slack_installation(
    slack_installation: SlackInstallationRequest,
    token: dict = Security(verify_token),  # noqa: ARG001
) -> OrganizationResponse:
    return org_service.add_organization_by_slack_installation(slack_installation)


@router.get("/slack/installation", status_code=status.HTTP_200_OK)
async def get_slack_installation_by_slack_workspace_id(
    workspace_id: str,
    token: dict = Security(verify_token),  # noqa: ARG001
) -> SlackInstallation:
    return org_service.get_slack_installation_by_slack_workspace_id(workspace_id)
