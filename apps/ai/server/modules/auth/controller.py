from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer

from modules.auth.service import AuthService
from modules.user.models.requests import UserRequest
from modules.user.models.responses import UserResponse
from utils.auth import VerifyToken

router = APIRouter(
    prefix="/auth",
    responses={404: {"description": "Not found"}},
)

token_auth_scheme = HTTPBearer()
auth_service = AuthService()


@router.post("/login", status_code=status.HTTP_202_ACCEPTED)
def login(
    user_request: UserRequest, token: str = Depends(token_auth_scheme)
) -> UserResponse:
    VerifyToken(token.credentials).verify()
    return auth_service.login(user_request)
