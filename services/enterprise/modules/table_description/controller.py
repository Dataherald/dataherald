from fastapi import APIRouter, Security, status

from modules.table_description.models.requests import (
    ScanRequest,
    TableDescriptionRequest,
)
from modules.table_description.models.responses import (
    ACTableDescriptionResponse,
    DatabaseDescriptionResponse,
    TableDescriptionResponse,
)
from modules.table_description.service import TableDescriptionService
from utils.auth import User, authenticate_user, get_api_key
from utils.validation import ObjectIdString

router = APIRouter(
    prefix="/api/table-descriptions",
    responses={404: {"description": "Not found"}},
)

ac_router = APIRouter(
    prefix="/table-descriptions",
    responses={404: {"description": "Not found"}},
)

table_description_service = TableDescriptionService()


@router.get("")
async def get_table_descriptions(
    db_connection_id: ObjectIdString,
    table_name: str = "",
    api_key: str = Security(get_api_key),
) -> list[TableDescriptionResponse]:
    return await table_description_service.get_table_descriptions(
        db_connection_id, table_name, api_key.organization_id
    )


@router.get("/{id}")
async def get_table_description(
    id: ObjectIdString,
    api_key: str = Security(get_api_key),
) -> TableDescriptionResponse:
    return await table_description_service.get_table_description(
        id, api_key.organization_id
    )


@router.post("/sync-schemas", status_code=status.HTTP_201_CREATED)
async def sync_table_descriptions_schemas(
    scan_request: ScanRequest, api_key: str = Security(get_api_key)
) -> list[TableDescriptionResponse]:
    return await table_description_service.sync_databases_schemas(
        scan_request, api_key.organization_id
    )


@router.put("/{id}")
async def update_table_description(
    id: ObjectIdString,
    table_description_request: TableDescriptionRequest,
    api_key: str = Security(get_api_key),
) -> TableDescriptionResponse:
    return await table_description_service.update_table_description(
        id, table_description_request, api_key.organization_id
    )


@ac_router.get("")
async def ac_get_table_descriptions(
    db_connection_id: ObjectIdString,
    table_name: str = "",
    user: User = Security(authenticate_user),
) -> list[ACTableDescriptionResponse]:
    return await table_description_service.get_table_descriptions(
        db_connection_id, table_name, user.organization_id
    )


@ac_router.get("/{id}")
async def ac_get_table_description(
    id: ObjectIdString, user: User = Security(authenticate_user)
) -> ACTableDescriptionResponse:
    return await table_description_service.get_table_description(
        id, user.organization_id
    )


# used for admin console, does not need api version endpoint
@ac_router.get("/database/list")
async def get_database_description_list(
    user: User = Security(authenticate_user),
) -> list[DatabaseDescriptionResponse]:
    return await table_description_service.get_database_description_list(
        user.organization_id
    )


@ac_router.post("/sync-schemas", status_code=status.HTTP_201_CREATED)
async def ac_sync_table_descriptions_schemas(
    scan_requests: ScanRequest, user: User = Security(authenticate_user)
) -> list[ACTableDescriptionResponse]:
    return await table_description_service.sync_databases_schemas(
        scan_requests, user.organization_id
    )


@ac_router.post("/refresh-all", status_code=status.HTTP_201_CREATED)
async def ac_refresh_table_descriptions(
    user: User = Security(authenticate_user),
) -> list[DatabaseDescriptionResponse]:
    return await table_description_service.refresh_table_description(
        user.organization_id
    )


@ac_router.put("/{id}")
async def ac_update_table_description(
    id: ObjectIdString,
    table_description_request: TableDescriptionRequest,
    user: User = Security(authenticate_user),
) -> ACTableDescriptionResponse:
    return await table_description_service.update_table_description(
        id, table_description_request, user.organization_id
    )
