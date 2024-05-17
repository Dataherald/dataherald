from fastapi import APIRouter, Form, Security, UploadFile, status
from pydantic import Json

from modules.db_connection.models.requests import DBConnectionRequest, SampleDBRequest
from modules.db_connection.models.responses import (
    DBConnectionResponse,
    SampleDBConnectionResponse,
)
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


@router.get("/sample")
async def get_sample_db_connections(
    api_key: str = Security(get_api_key),  # noqa: ARG001
) -> list[SampleDBConnectionResponse]:
    return db_connection_service.get_sample_db_connections()


@router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_db_connection(
    id: ObjectIdString,
    api_key: str = Security(get_api_key),
) -> DBConnectionResponse:
    return db_connection_service.get_db_connection(id, api_key.organization_id)


@router.post("", status_code=status.HTTP_201_CREATED)
async def add_db_connection(
    request: DBConnectionRequest,
    api_key: str = Security(get_api_key),
) -> DBConnectionResponse:
    return await db_connection_service.add_db_connection(
        request, api_key.organization_id
    )


@router.post("/sample", status_code=status.HTTP_201_CREATED)
async def add_sample_db_connection(
    request: SampleDBRequest,
    api_key: str = Security(get_api_key),
) -> DBConnectionResponse:
    return await db_connection_service.add_sample_db_connection(
        request, api_key.organization_id
    )


@router.put("/{id}", status_code=status.HTTP_200_OK)
async def update_db_connection(
    id: ObjectIdString,
    request: DBConnectionRequest,
    api_key: str = Security(get_api_key),
) -> DBConnectionResponse:
    return await db_connection_service.update_db_connection(
        id, request, api_key.organization_id
    )


@ac_router.get("", status_code=status.HTTP_200_OK)
async def ac_get_db_connections(
    user: User = Security(authenticate_user),
) -> list[DBConnectionResponse]:
    return db_connection_service.get_db_connections(user.organization_id)


@ac_router.get("/sample")
async def ac_get_sample_db_connections(
    user: User = Security(authenticate_user),  # noqa: ARG001
) -> list[SampleDBConnectionResponse]:
    return db_connection_service.get_sample_db_connections()


@ac_router.get("/{id}", status_code=status.HTTP_200_OK)
async def ac_get_db_connection(
    id: ObjectIdString,
    user: User = Security(authenticate_user),
) -> DBConnectionResponse:
    return db_connection_service.get_db_connection(id, user.organization_id)


@ac_router.post("", status_code=status.HTTP_201_CREATED)
async def ac_add_db_connection(
    request_json: Json = Form(...),
    file: UploadFile = None,
    user: User = Security(authenticate_user),
) -> DBConnectionResponse:
    request = DBConnectionRequest(**request_json)
    return await db_connection_service.add_db_connection(
        request, user.organization_id, file
    )


@ac_router.put("/{id}", status_code=status.HTTP_200_OK)
async def ac_update_db_connection(
    id: ObjectIdString,
    request_json: Json = Form(...),
    file: UploadFile = None,
    user: User = Security(authenticate_user),
) -> DBConnectionResponse:
    request = DBConnectionRequest(**request_json)
    return await db_connection_service.update_db_connection(
        id, request, user.organization_id, file
    )


@ac_router.post("/sample", status_code=status.HTTP_201_CREATED)
async def ac_add_sample_db_connection(
    request: SampleDBRequest,
    user: User = Security(authenticate_user),
) -> DBConnectionResponse:
    return await db_connection_service.add_sample_db_connection(
        request, user.organization_id
    )
