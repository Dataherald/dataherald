from typing import List

from fastapi import APIRouter, Depends, Security, status
from fastapi.security import HTTPBearer

from modules.generation.models.entities import GenerationStatus
from modules.golden_sql.models.requests import GoldenSQLRequest
from modules.golden_sql.models.responses import (
    AdminConsoleGoldenSqlResponse,
    GoldenSQLResponse,
)
from modules.golden_sql.service import GoldenSQLService
from utils.auth import Authorize, VerifyToken, get_api_key
from utils.validation import ObjectIdString

router = APIRouter(
    prefix="/api/golden-sqls",
    responses={404: {"description": "Not found"}},
)

ac_router = APIRouter(
    prefix="/golden-sqls",
    responses={404: {"description": "Not found"}},
)

token_auth_scheme = HTTPBearer()
golden_sql_service = GoldenSQLService()
authorize = Authorize()


@router.get("")
async def get_golden_sqls(
    page: int = 0,
    page_size: int = 20,
    order: str = "created_at",
    ascend: bool = False,
    api_key: str = Security(get_api_key),
) -> list[GoldenSQLResponse]:
    return golden_sql_service.get_golden_sqls(
        page=page,
        page_size=page_size,
        order=order,
        ascend=ascend,
        org_id=api_key.organization_id,
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
    token: str = Depends(token_auth_scheme),
) -> list[AdminConsoleGoldenSqlResponse]:
    org_id = authorize.user(VerifyToken(token.credentials).verify()).organization_id
    return golden_sql_service.get_golden_sqls(
        page=page, page_size=page_size, order=order, ascend=ascend, org_id=org_id
    )


@ac_router.get("/{id}")
async def ac_get_golden_sql(
    id: ObjectIdString, token: str = Depends(token_auth_scheme)
) -> AdminConsoleGoldenSqlResponse:
    org_id = authorize.user(VerifyToken(token.credentials).verify()).organization_id
    return golden_sql_service.get_golden_sql(id, org_id)


@ac_router.post("", status_code=status.HTTP_201_CREATED)
async def ac_add_user_upload_golden_sql(
    golden_sql_requests: List[GoldenSQLRequest], token: str = Depends(token_auth_scheme)
) -> List[AdminConsoleGoldenSqlResponse]:
    org_id = authorize.user(VerifyToken(token.credentials).verify()).organization_id
    return await golden_sql_service.add_user_upload_golden_sql(
        golden_sql_requests, org_id
    )


@ac_router.delete("/{id}")
async def ac_delete_golden_sql(
    id: ObjectIdString, token: str = Depends(token_auth_scheme)
):
    org_id = authorize.user(VerifyToken(token.credentials).verify()).organization_id
    return await golden_sql_service.delete_golden_sql(
        id, org_id, GenerationStatus.NOT_VERIFIED
    )
