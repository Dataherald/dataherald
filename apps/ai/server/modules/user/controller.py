from fastapi import APIRouter, status

from modules.user.models.requests import UserRequest
from modules.user.models.responses import UserResponse
from modules.user.service import UserService

router = APIRouter(
    prefix="/user",
    responses={404: {"description": "Not found"}},
)

user_service = UserService()


@router.get("/list")
async def list_users(organization: str = None) -> list[UserResponse]:
    return user_service.list_users(organization)


@router.get("/{id}")
async def get_user(id: str) -> UserResponse:
    return user_service.get_user(id)


@router.delete("/{id}")
async def delete_user(id: str):
    return user_service.delete_user(id)


@router.put("/{id}")
async def update_user(id: str, user_request: UserRequest) -> UserResponse:
    return user_service.update_user(id, user_request.dict(), exclude={"id"})


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_user(user_request: UserRequest) -> UserResponse:
    return user_service.add_user(user_request.dict())
