from fastapi import APIRouter, Depends, Form, UploadFile, status
from fastapi.security import HTTPBearer
from pydantic import Json

from modules.database.models.requests import (
    DatabaseConnectionRequest,
    ScanRequest,
    TableDescriptionRequest,
)
from modules.database.models.responses import ScannedDBResponse
from modules.database.service import DatabaseService
from utils.auth import Authorize, VerifyToken

router = APIRouter(
    prefix="/database",
    responses={404: {"description": "Not found"}},
)

token_auth_scheme = HTTPBearer()
authorize = Authorize()
database_service = DatabaseService()


@router.get("/list", status_code=status.HTTP_200_OK)
async def get_scanned_databases(
    token: str = Depends(token_auth_scheme),
) -> list[ScannedDBResponse]:
    organization_id = authorize.user_and_get_org_id(
        VerifyToken(token.credentials).verify()
    )
    return await database_service.get_scanned_databases(organization_id)


@router.patch("{db_alias}/description", status_code=status.HTTP_200_OK)
async def add_scanned_databases_description(
    db_alias: str,
    table_description_request: TableDescriptionRequest,
    token: str = Depends(token_auth_scheme),
) -> bool:
    authorize.user(VerifyToken(token.credentials).verify())
    return await database_service.add_scanned_databases_description(
        db_alias, table_description_request
    )


@router.post("/scan", status_code=status.HTTP_201_CREATED)
async def scan_database(
    scan_request: ScanRequest, token: str = Depends(token_auth_scheme)
) -> bool:
    authorize.user(VerifyToken(token.credentials).verify())
    return await database_service.scan_database(scan_request)


@router.post("", status_code=status.HTTP_201_CREATED)
async def add_database_connection(
    database_connection_request: Json = Form(),
    file: UploadFile = None,
    token: str = Depends(token_auth_scheme),
) -> bool:
    database_connection_request = DatabaseConnectionRequest(
        **database_connection_request
    )
    user = authorize.user(VerifyToken(token.credentials).verify())
    organization = authorize.get_organization_by_user(user)
    return await database_service.add_database_connection(
        database_connection_request, organization, file
    )
