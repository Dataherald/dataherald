from fastapi import APIRouter, Form, Security, UploadFile, status
from pydantic import Json

from modules.db_connection.models.requests import DBConnectionRequest
from modules.db_connection.models.responses import DBConnectionResponse
from modules.db_connection.service import DBConnectionService
from utils.auth import User, authenticate_user, get_api_key
from utils.validation import ObjectIdString

router = APIRouter(
    prefix="/api/database-connections",
    responses={404: {"description": "Not found"}},
)

ac_router = APIRouter(
    prefix="/database-connections",
    responses={404: {"description": "Not found"}},
)

db_connection_service = DBConnectionService()


@router.get("", status_code=status.HTTP_200_OK)
async def get_db_connections(
    api_key: str = Security(get_api_key),
) -> list[DBConnectionResponse]:
    return db_connection_service.get_db_connections(api_key.organization_id)


@router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_db_connection(
    id: ObjectIdString,
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
    id: ObjectIdString,
    db_connection_request: DBConnectionRequest,
    api_key: str = Security(get_api_key),
) -> DBConnectionResponse:
    return await db_connection_service.update_db_connection(
        id, db_connection_request, api_key.organization_id
    )


@ac_router.get("", status_code=status.HTTP_200_OK)
async def ac_get_db_connections(
    user: User = Security(authenticate_user),
) -> list[DBConnectionResponse]:
    return db_connection_service.get_db_connections(user.organization_id)


@ac_router.get("/{id}", status_code=status.HTTP_200_OK)
async def ac_get_db_connection(
    id: ObjectIdString,
    user: User = Security(authenticate_user),
) -> DBConnectionResponse:

    return db_connection_service.get_db_connection(id, user.organization_id)


@ac_router.post("", status_code=status.HTTP_201_CREATED)
async def ac_add_db_connection(
    db_connection_request_json: Json = Form(...),
    file: UploadFile = None,
    user: User = Security(authenticate_user),
) -> DBConnectionResponse:
    db_connection_request = DBConnectionRequest(**db_connection_request_json)
    return await db_connection_service.add_db_connection(
        db_connection_request, user.organization_id, file
    )


@ac_router.put("/{id}", status_code=status.HTTP_200_OK)
async def ac_update_db_connection(
    id: ObjectIdString,
    db_connection_request_json: Json = Form(...),
    file: UploadFile = None,
    user: User = Security(authenticate_user),
) -> DBConnectionResponse:
    db_connection_request = DBConnectionRequest(**db_connection_request_json)
    return await db_connection_service.update_db_connection(
        id, db_connection_request, user.organization_id, file
    )
