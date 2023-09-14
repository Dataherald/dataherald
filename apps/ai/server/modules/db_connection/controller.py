from fastapi import APIRouter, Depends, Form, UploadFile, status
from fastapi.security import HTTPBearer
from pydantic import Json

from modules.db_connection.models.requests import DBConnectionRequest
from modules.db_connection.models.responses import DBConnectionResponse
from modules.db_connection.service import DBConnectionService
from utils.auth import Authorize, VerifyToken

router = APIRouter(
    prefix="/database-connection",
    responses={404: {"description": "Not found"}},
)

token_auth_scheme = HTTPBearer()
authorize = Authorize()
db_connection_service = DBConnectionService()


@router.get("/list", status_code=status.HTTP_200_OK)
async def get_db_connections(
    token: str = Depends(token_auth_scheme),
) -> list[DBConnectionResponse]:
    org_id = authorize.user_and_get_org_id(VerifyToken(token.credentials).verify())
    return db_connection_service.get_db_connections(org_id)


@router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_db_connection(
    id: str, token: str = Depends(token_auth_scheme)
) -> DBConnectionResponse:
    org_id = authorize.user_and_get_org_id(VerifyToken(token.credentials).verify())
    authorize.db_connection_in_organization(id, org_id)
    return db_connection_service.get_db_connection(id)


@router.post("", status_code=status.HTTP_201_CREATED)
async def add_db_connection(
    db_connection_request_json: Json = Form(),
    file: UploadFile = None,
    token: str = Depends(token_auth_scheme),
) -> DBConnectionResponse:
    org_id = authorize.user_and_get_org_id(VerifyToken(token.credentials).verify())
    return db_connection_service.add_db_connection(
        db_connection_request_json, org_id, file
    )


@router.put("/{id}", status_code=status.HTTP_200_OK)
async def update_db_connection(
    id: str,
    db_connection_request: DBConnectionRequest,
    token: str = Depends(token_auth_scheme),
) -> DBConnectionResponse:
    org_id = authorize.user_and_get_org_id(VerifyToken(token.credentials).verify())
    authorize.db_connection_in_organization(id, org_id)
    return db_connection_service.update_db_connection(id, db_connection_request)
