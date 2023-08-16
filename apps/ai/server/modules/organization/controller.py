from fastapi import APIRouter, status

from modules.organization.models.requests import OrganizationRequest
from modules.organization.service import OrganizationService

router = APIRouter(
    prefix="/organization",
    responses={404: {"description": "Not found"}},
)

org_service = OrganizationService()


@router.get("/list")
async def list_organizations():
    return org_service.list_organizations()


@router.get("/{id}")
async def get_organization(id: str):
    return org_service.get_organization(id)


@router.delete("/{id}")
async def delete_organization(id: str):
    return org_service.delete_organization(id)


@router.put("/{id}")
async def update_organization(id: str, org_request: OrganizationRequest):
    return org_service.update_organization(id, org_request)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_organization(org_request: OrganizationRequest):
    return org_service.add_organization(org_request)
