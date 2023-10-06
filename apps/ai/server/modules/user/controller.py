from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer

from modules.user.models.requests import UserRequest
from modules.user.models.responses import UserResponse
from modules.user.service import UserService
from utils.auth import Authorize, VerifyToken

router = APIRouter(
    prefix="/user",
    responses={404: {"description": "Not found"}},
)

token_auth_scheme = HTTPBearer()
user_service = UserService()
authorize = Authorize()


@router.get("/list")
async def get_users(token: str = Depends(token_auth_scheme)) -> list[UserResponse]:
    org_id = authorize.user(VerifyToken(token.credentials).verify()).organization_id
    return user_service.get_users(org_id)


@router.get("/{id}")
async def get_user(id: str, token: str = Depends(token_auth_scheme)) -> UserResponse:
    org_id = authorize.user(VerifyToken(token.credentials).verify()).organization_id
    authorize.user_in_organization(id, org_id)
    return user_service.get_user(id)


@router.post("", status_code=status.HTTP_201_CREATED)
async def add_user(
    user_request: UserRequest, token: str = Depends(token_auth_scheme)
) -> UserResponse:
    org_id = authorize.user(VerifyToken(token.credentials).verify()).organization_id
    return user_service.add_user(user_request, org_id)


@router.put("/{id}")
async def update_user(
    id: str, user_request: UserRequest, token: str = Depends(token_auth_scheme)
) -> UserResponse:
    org_id = authorize.user(VerifyToken(token.credentials).verify()).organization_id
    authorize.user_in_organization(id, org_id)
    return user_service.update_user(id, user_request)


@router.delete("/{id}")
async def delete_user(id: str, token: str = Depends(token_auth_scheme)) -> dict:
    org_id = authorize.user(VerifyToken(token.credentials).verify()).organization_id
    authorize.user_in_organization(id, org_id)
    return user_service.delete_user(id)
