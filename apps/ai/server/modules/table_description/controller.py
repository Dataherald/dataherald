from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer

from modules.table_description.models.requests import (
    ScanRequest,
    TableDescriptionRequest,
)
from modules.table_description.models.responses import (
    DatabaseDescriptionResponse,
    TableDescriptionResponse,
)
from modules.table_description.service import TableDescriptionService
from utils.auth import Authorize, VerifyToken

router = APIRouter(
    prefix="/table-description",
    responses={404: {"description": "Not found"}},
)

token_auth_scheme = HTTPBearer()
authorize = Authorize()
table_description_service = TableDescriptionService()


@router.get("/list", status_code=status.HTTP_200_OK)
async def get_table_descriptions(
    table_name: str = "",
    token: str = Depends(token_auth_scheme),
) -> list[TableDescriptionResponse]:
    user = authorize.user(VerifyToken(token.credentials).verify())
    organization = authorize.get_organization_by_user(user)
    return await table_description_service.get_table_descriptions(
        table_name, str(organization.db_connection_id)
    )


@router.get("/database/list", status_code=status.HTTP_200_OK)
async def get_database_table_descriptions(
    token: str = Depends(token_auth_scheme),
) -> list[DatabaseDescriptionResponse]:
    user = authorize.user(VerifyToken(token.credentials).verify())
    organization = authorize.get_organization_by_user(user)
    return await table_description_service.get_database_table_descriptions(
        str(organization.db_connection_id)
    )


@router.post("/scan", status_code=status.HTTP_201_CREATED)
async def scan_table_descriptions(
    scan_request: ScanRequest, token: str = Depends(token_auth_scheme)
):
    authorize.user(VerifyToken(token.credentials).verify())
    return await table_description_service.scan_table_descriptions(scan_request)


@router.patch("/{id}", status_code=status.HTTP_200_OK)
async def update_table_description(
    id: str,
    table_description_request: TableDescriptionRequest,
    token: str = Depends(token_auth_scheme),
) -> TableDescriptionResponse:
    org_id = authorize.user_and_get_org_id(VerifyToken(token.credentials).verify())
    authorize.table_description_in_organization(id, org_id)
    return await table_description_service.update_table_description(
        id, table_description_request
    )
