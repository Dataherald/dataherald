from fastapi import APIRouter, Depends, Security, status
from fastapi.security import HTTPBearer

from modules.db_connection.models.requests import DBConnectionRequest
from modules.db_connection.models.responses import DBConnectionResponse
from modules.db_connection.service import DBConnectionService
from utils.auth import Authorize, VerifyToken, get_api_key

router = APIRouter(
    prefix="/api/database-connections",
    responses={404: {"description": "Not found"}},
)

ac_router = APIRouter(
    prefix="/database-connections",
    responses={404: {"description": "Not found"}},
)

token_auth_scheme = HTTPBearer()
authorize = Authorize()
db_connection_service = DBConnectionService()


@router.get("", status_code=status.HTTP_200_OK)
async def get_db_connections(
    api_key: str = Security(get_api_key),
) -> list[DBConnectionResponse]:
    return db_connection_service.get_db_connections(api_key.organization_id)


@router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_db_connection(
    id: str,
    api_key: str = Security(get_api_key),
) -> DBConnectionResponse:
    return db_connection_service.get_db_connection(id, api_key.organization_id)


@router.post("", status_code=status.HTTP_201_CREATED)
async def add_db_connection(
    db_connection_request: DBConnectionRequest,
    api_key: str = Security(get_api_key),
) -> DBConnectionResponse:
    return await db_connection_service.add_db_connection(
        db_connection_request, api_key.organization_id
    )


@router.put("/{id}", status_code=status.HTTP_200_OK)
async def update_db_connection(
    id: str,
    db_connection_request: DBConnectionRequest,
    api_key: str = Security(get_api_key),
) -> DBConnectionResponse:
    return await db_connection_service.update_db_connection(
        id, db_connection_request, api_key.organization_id
    )


@ac_router.get("", status_code=status.HTTP_200_OK)
async def ac_get_db_connections(
    token: str = Depends(token_auth_scheme),
) -> list[DBConnectionResponse]:
    org_id = authorize.user(VerifyToken(token.credentials).verify()).organization_id
    return db_connection_service.get_db_connections(org_id)


@ac_router.get("/{id}", status_code=status.HTTP_200_OK)
async def ac_get_db_connection(
    id: str, token: str = Depends(token_auth_scheme)
) -> DBConnectionResponse:
    org_id = authorize.user(VerifyToken(token.credentials).verify()).organization_id
    return db_connection_service.get_db_connection(id, org_id)


@ac_router.post("", status_code=status.HTTP_201_CREATED)
async def ac_add_db_connection(
    db_connection_request: DBConnectionRequest,
    token: str = Depends(token_auth_scheme),
) -> DBConnectionResponse:
    user = authorize.user(VerifyToken(token.credentials).verify())
    return await db_connection_service.add_db_connection(
        db_connection_request, user.organization_id
    )


@ac_router.put("/{id}", status_code=status.HTTP_200_OK)
async def ac_update_db_connection(
    id: str,
    db_connection_request: DBConnectionRequest,
    token: str = Depends(token_auth_scheme),
) -> DBConnectionResponse:
    user = authorize.user(VerifyToken(token.credentials).verify())
    return await db_connection_service.update_db_connection(
        id, db_connection_request, user.organization_id
    )
