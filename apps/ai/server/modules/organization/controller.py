from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer

from modules.organization.models.requests import OrganizationRequest
from modules.organization.models.responses import OrganizationResponse
from modules.organization.service import OrganizationService
from utils.auth import VerifyToken

router = APIRouter(
    prefix="/organization",
    responses={404: {"description": "Not found"}},
)

token_auth_scheme = HTTPBearer()
org_service = OrganizationService()


@router.get("/list")
async def list_organizations(
    token: str = Depends(token_auth_scheme),
) -> list[OrganizationResponse]:
    VerifyToken(token.credentials)
    return org_service.list_organizations()


@router.get("/{id}")
async def get_organization(
    id: str, token: str = Depends(token_auth_scheme)
) -> OrganizationResponse:
    VerifyToken(token.credentials)
    return org_service.get_organization(id)


@router.delete("/{id}")
async def delete_organization(id: str, token: str = Depends(token_auth_scheme)):
    VerifyToken(token.credentials)
    return org_service.delete_organization(id)


@router.put("/{id}")
async def update_organization(
    id: str, org_request: dict, token: str = Depends(token_auth_scheme)
) -> OrganizationResponse:
    VerifyToken(token.credentials)
    return org_service.update_organization(id, org_request)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_organization(
    org_request: OrganizationRequest, token: str = Depends(token_auth_scheme)
) -> OrganizationResponse:
    VerifyToken(token.credentials)
    return org_service.add_organization(org_request)
