from typing import List

from fastapi import APIRouter, Security, status

from modules.generation.models.entities import GenerationStatus
from modules.golden_sql.models.requests import GoldenSQLRequest
from modules.golden_sql.models.responses import (
    ACGoldenSQLResponse,
    GoldenSQLResponse,
)
from modules.golden_sql.service import GoldenSQLService
from utils.auth import User, authenticate_user, get_api_key
from utils.validation import ObjectIdString

router = APIRouter(
    prefix="/api/golden-sqls",
    responses={404: {"description": "Not found"}},
)

ac_router = APIRouter(
    prefix="/golden-sqls",
    responses={404: {"description": "Not found"}},
)

golden_sql_service = GoldenSQLService()


@router.get("")
async def get_golden_sqls(
    page: int = 0,
    page_size: int = 20,
    order: str = "created_at",
    ascend: bool = False,
    search_term: str = "",
    db_connection_id: str = None,
    api_key: str = Security(get_api_key),
) -> list[GoldenSQLResponse]:
    return golden_sql_service.get_golden_sqls(
        page=page,
        page_size=page_size,
        order=order,
        ascend=ascend,
        org_id=api_key.organization_id,
        search_term=search_term,
        db_connection_id=db_connection_id,
    )


@router.get("/{id}")
async def get_golden_sql(
    id: ObjectIdString, api_key: str = Security(get_api_key)
) -> GoldenSQLResponse:
    return golden_sql_service.get_golden_sql(id, api_key.organization_id)


@router.post("", status_code=status.HTTP_201_CREATED)
async def add_user_upload_golden_sql(
    golden_sql_requests: List[GoldenSQLRequest], api_key: str = Security(get_api_key)
) -> List[GoldenSQLResponse]:
    return await golden_sql_service.add_user_upload_golden_sql(
        golden_sql_requests, api_key.organization_id
    )


@router.delete("/{id}")
async def delete_golden_sql(id: ObjectIdString, api_key: str = Security(get_api_key)):
    return await golden_sql_service.delete_golden_sql(
        id, api_key.organization_id, GenerationStatus.NOT_VERIFIED
    )


@ac_router.get("")
async def ac_get_golden_sqls(
    page: int = 0,
    page_size: int = 20,
    order: str = "created_at",
    ascend: bool = False,
    search_term: str = "",
    db_connection_id: str = None,
    user: User = Security(authenticate_user),
) -> list[ACGoldenSQLResponse]:
    return golden_sql_service.get_golden_sqls(
        page=page,
        page_size=page_size,
        order=order,
        ascend=ascend,
        org_id=user.organization_id,
        search_term=search_term,
        db_connection_id=db_connection_id,
    )


@ac_router.get("/{id}")
async def ac_get_golden_sql(
    id: ObjectIdString, user: User = Security(authenticate_user)
) -> ACGoldenSQLResponse:
    return golden_sql_service.get_golden_sql(id, user.organization_id)


@ac_router.post("", status_code=status.HTTP_201_CREATED)
async def ac_add_user_upload_golden_sql(
    golden_sql_requests: List[GoldenSQLRequest],
    user: User = Security(authenticate_user),
) -> List[ACGoldenSQLResponse]:
    return await golden_sql_service.add_user_upload_golden_sql(
        golden_sql_requests, user.organization_id
    )


@ac_router.delete("/{id}")
async def ac_delete_golden_sql(
    id: ObjectIdString, user: User = Security(authenticate_user)
):
    return await golden_sql_service.delete_golden_sql(
        id, user.organization_id, GenerationStatus.NOT_VERIFIED
    )
