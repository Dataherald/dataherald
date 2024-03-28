from fastapi import APIRouter, Security, status

from modules.auth.service import AuthService
from modules.user.models.requests import UserRequest
from modules.user.models.responses import UserResponse
from utils.auth import verify_token

router = APIRouter(
    prefix="/auth",
    responses={404: {"description": "Not found"}},
)

auth_service = AuthService()


@router.post("/login", status_code=status.HTTP_202_ACCEPTED)
def login(
    user_request: UserRequest, token: str = Security(verify_token)  # noqa: ARG001
) -> UserResponse:
    return auth_service.login(user_request)
