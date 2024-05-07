from fastapi import APIRouter, Security, status

from modules.user.models.requests import UserOrganizationRequest, UserRequest
from modules.user.models.responses import UserResponse
from modules.user.service import UserService
from utils.auth import Authorize, User, authenticate_user
from utils.validation import ObjectIdString

router = APIRouter(
    prefix="/users",
    responses={404: {"description": "Not found"}},
)

user_service = UserService()
authorize = Authorize()


@router.get("")
async def get_users(
    session_user: User = Security(authenticate_user),
) -> list[UserResponse]:
    return user_service.get_users(session_user.organization_id)


@router.get("/{id}")
async def get_user(
    id: ObjectIdString, session_user: User = Security(authenticate_user)
) -> UserResponse:
    return user_service.get_user(id, session_user.organization_id)


@router.post("", status_code=status.HTTP_201_CREATED)
async def add_user(
    new_user_request: UserRequest, session_user: User = Security(authenticate_user)
) -> UserResponse:
    authorize.is_admin_user(session_user)
    return user_service.add_user(new_user_request)


@router.put("/{id}")
async def update_user(
    id: ObjectIdString,
    user_request: UserRequest,
    session_user: User = Security(authenticate_user),
) -> UserResponse:
    authorize.user_in_organization(id, session_user.organization_id)
    # TODO - check if the session_user is an admin or not -- we can't have several auth checks cause they're raising HTTP exceptions
    return user_service.update_user(
        id,
        user_request,
    )


@router.patch("/{id}")
async def update_user_organization(
    id: ObjectIdString,
    user_organization_request: UserOrganizationRequest,
    session_user: User = Security(authenticate_user),
) -> UserResponse:
    authorize.is_admin_user(session_user)
    return user_service.update_user_organization(id, user_organization_request)


@router.delete("/{id}")
async def delete_user(
    id: ObjectIdString, session_user: User = Security(authenticate_user)
) -> dict:
    authorize.is_not_self(session_user.id, id)
    return user_service.delete_user(id, session_user.organization_id)


@router.post("/invite")
async def invite_user_to_org(
    new_user_request: UserRequest, session_user: User = Security(authenticate_user)
) -> UserResponse:
    authorize.user_in_organization(session_user.id, session_user.organization_id)
    return user_service.invite_user_to_org(
        new_user_request, session_user.organization_id
    )
