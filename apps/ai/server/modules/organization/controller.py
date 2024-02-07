from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer

from modules.organization.models.entities import SlackInstallation
from modules.organization.models.requests import (
    OrganizationRequest,
    SlackInstallationRequest,
)
from modules.organization.models.responses import OrganizationResponse
from modules.organization.service import OrganizationService
from utils.auth import Authorize, VerifyToken
from utils.validation import ObjectIdString

router = APIRouter(
    prefix="/organizations",
    responses={404: {"description": "Not found"}},
)

authorize = Authorize()
token_auth_scheme = HTTPBearer()
org_service = OrganizationService()


@router.get("")
async def get_organizations(
    token: str = Depends(token_auth_scheme),
) -> list[OrganizationResponse]:
    authorize.is_admin_user(authorize.user(VerifyToken(token.credentials).verify()))
    return org_service.get_organizations()


@router.get("/{id}")
async def get_organization(
    id: ObjectIdString, token: str = Depends(token_auth_scheme)
) -> OrganizationResponse:
    user_id = authorize.user(VerifyToken(token.credentials).verify()).id
    authorize.user_in_organization(user_id, id)
    return org_service.get_organization(id)


@router.post("", status_code=status.HTTP_201_CREATED)
async def add_organization(
    org_request: OrganizationRequest, token: str = Depends(token_auth_scheme)
) -> OrganizationResponse:
    session_user = authorize.user(VerifyToken(token.credentials).verify())
    authorize.is_admin_user(session_user)
    return org_service.add_organization(
        OrganizationRequest(
            **org_request.dict(exclude={"owner"}), owner=session_user.id
        )
    )


@router.put("/{id}")
async def update_organization(
    id: ObjectIdString,
    org_request: OrganizationRequest,
    token: str = Depends(token_auth_scheme),
) -> OrganizationResponse:
    user_id = authorize.user(VerifyToken(token.credentials).verify()).id
    authorize.user_in_organization(user_id, id)
    return org_service.update_organization(id, org_request)


@router.delete("/{id}")
async def delete_organization(
    id: ObjectIdString, token: str = Depends(token_auth_scheme)
):
    user = authorize.user(VerifyToken(token.credentials).verify())
    authorize.is_admin_user(user)
    authorize.is_not_self(user.organization_id, id)
    return org_service.delete_organization(id)


@router.post("/slack/installation", status_code=status.HTTP_201_CREATED)
async def add_organization_by_slack_installation(
    slack_installation: SlackInstallationRequest,
    token: str = Depends(token_auth_scheme),
) -> OrganizationResponse:
    VerifyToken(token.credentials).verify()
    return org_service.add_organization_by_slack_installation(slack_installation)


@router.get("/slack/installation", status_code=status.HTTP_200_OK)
async def get_slack_installation_by_slack_workspace_id(
    workspace_id: str,
    token: str = Depends(token_auth_scheme),
) -> SlackInstallation:
    VerifyToken(token.credentials).verify()
    return org_service.get_slack_installation_by_slack_workspace_id(workspace_id)
