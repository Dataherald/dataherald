from typing import List

from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer

from modules.golden_sql.models.entities import GoldenSQLSource
from modules.golden_sql.models.requests import GoldenSQLRequest
from modules.golden_sql.models.responses import GoldenSQLResponse
from modules.golden_sql.service import GoldenSQLService
from utils.auth import Authorize, VerifyToken

router = APIRouter(
    prefix="/golden-sql",
    responses={404: {"description": "Not found"}},
)


token_auth_scheme = HTTPBearer()
golden_sql_service = GoldenSQLService()
authorize = Authorize()


@router.get("/list")
async def get_golden_sqls(
    page: int = 0,
    page_size: int = 20,
    order: str = "created_time",
    ascend: bool = True,
    token: str = Depends(token_auth_scheme),
) -> list[GoldenSQLResponse]:
    org_id = authorize.user_and_get_org_id(VerifyToken(token.credentials).verify())
    return golden_sql_service.get_golden_sqls(
        page=page, page_size=page_size, order=order, ascend=ascend, org_id=org_id
    )


@router.get("/{id}")
async def get_golden_sql(
    id: str, token: str = Depends(token_auth_scheme)
) -> GoldenSQLResponse:
    org_id = authorize.user_and_get_org_id(VerifyToken(token.credentials).verify())
    authorize.golden_sql_in_organization(id, org_id)
    return golden_sql_service.get_golden_sql(id)


@router.post("", status_code=status.HTTP_201_CREATED)
async def add_golden_sql(
    golden_sql_requests: List[GoldenSQLRequest], token: str = Depends(token_auth_scheme)
) -> GoldenSQLResponse:
    org_id = authorize.user_and_get_org_id(VerifyToken(token.credentials).verify())
    return await golden_sql_service.add_golden_sql(
        golden_sql_requests, org_id, GoldenSQLSource.user_upload
    )


@router.delete("/{id}")
async def delete_golden_sql(id: str, token: str = Depends(token_auth_scheme)):
    org_id = authorize.user_and_get_org_id(VerifyToken(token.credentials).verify())
    authorize.golden_sql_in_organization(id, org_id)
    return await golden_sql_service.delete_golden_sql(id)
