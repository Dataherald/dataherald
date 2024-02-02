from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer

from modules.user.models.requests import UserOrganizationRequest, UserRequest
from modules.user.models.responses import UserResponse
from modules.user.service import UserService
from utils.auth import Authorize, VerifyToken
from utils.validation import ObjectIdString

router = APIRouter(
    prefix="/users",
    responses={404: {"description": "Not found"}},
)

token_auth_scheme = HTTPBearer()
user_service = UserService()
authorize = Authorize()


@router.get("")
async def get_users(token: str = Depends(token_auth_scheme)) -> list[UserResponse]:
    user = authorize.user(VerifyToken(token.credentials).verify())
    return user_service.get_users(user.organization_id)


@router.get("/{id}")
async def get_user(
    id: ObjectIdString, token: str = Depends(token_auth_scheme)
) -> UserResponse:
    user = authorize.user(VerifyToken(token.credentials).verify())
    return user_service.get_user(id, user.organization_id)


@router.post("", status_code=status.HTTP_201_CREATED)
async def add_user(
    new_user_request: UserRequest, token: str = Depends(token_auth_scheme)
) -> UserResponse:
    authorize.is_admin_user(VerifyToken(token.credentials).verify())
    return user_service.add_user(new_user_request)


@router.put("/{id}")
async def update_user(
    id: ObjectIdString,
    user_request: UserRequest,
    token: str = Depends(token_auth_scheme),
) -> UserResponse:
    session_user = authorize.user(VerifyToken(token.credentials).verify())
    authorize.user_in_organization(id, session_user.organization_id)
    # TODO - check if the user is an admin or not -- currently we can't have several auth checks cause they're raising HTTP exceptions
    return user_service.update_user(
        id,
        user_request,
    )


@router.patch("/{id}")
async def update_user_organization(
    id: ObjectIdString,
    user_organization_request: UserOrganizationRequest,
    token: str = Depends(token_auth_scheme),
) -> UserResponse:
    session_user = authorize.user(VerifyToken(token.credentials).verify())
    authorize.is_admin_user(session_user)
    return user_service.update_user_organization(id, user_organization_request)


@router.delete("/{id}")
async def delete_user(
    id: ObjectIdString, token: str = Depends(token_auth_scheme)
) -> dict:
    user = authorize.user(VerifyToken(token.credentials).verify())
    authorize.is_not_self(user.id, id)
    return user_service.delete_user(id, user.organization_id)


@router.post("/invite")
async def invite_user_to_org(
    new_user_request: UserRequest,
    token: str = Depends(token_auth_scheme),
) -> UserResponse:
    session_user = authorize.user(VerifyToken(token.credentials).verify())
    authorize.user_in_organization(session_user.id, session_user.organization_id)
    return user_service.invite_user_to_org(
        new_user_request, session_user.organization_id
    )
