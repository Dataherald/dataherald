from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

from modules.database.models.requests import TableDescriptionRequest
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


@router.get("/list")
async def get_scanned_databases(
    token: str = Depends(token_auth_scheme),
) -> list[ScannedDBResponse]:
    organization_id = authorize.user_and_get_org_id(
        VerifyToken(token.credentials).verify()
    )
    return await database_service.get_scanned_databases(organization_id)


@router.patch("/description/{db_name}/{table_name}")
async def add_scanned_databases_description(
    db_name: str, table_name: str, table_description_request: TableDescriptionRequest
) -> bool:
    return await database_service.add_scanned_databases_description(
        db_name, table_name, table_description_request
    )
