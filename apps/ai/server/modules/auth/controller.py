from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer

from modules.auth.models.requests import AuthUserRequest
from modules.auth.service import AuthService
from modules.user.models.responses import UserResponse
from utils.auth import VerifyToken

router = APIRouter(
    prefix="/auth",
    responses={404: {"description": "Not found"}},
)

token_auth_scheme = HTTPBearer()


@router.post("/login", status_code=status.HTTP_202_ACCEPTED)
def login(
    user_request: AuthUserRequest, token: str = Depends(token_auth_scheme)
) -> UserResponse:
    result = VerifyToken(token.credentials).verify()
    if result.get("status"):
        raise HTTPException(status_code=400, detail="Bad Request")

    return AuthService().login(user_request)
