from typing import List

from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer

from modules.key.models.requests import KeyGenerationRequest
from modules.key.models.responses import KeyPreviewResponse, KeyResponse
from modules.key.service import KeyService
from utils.auth import Authorize, VerifyToken
from utils.validation import ObjectIdString

router = APIRouter(
    prefix="/keys",
    responses={404: {"description": "Not found"}},
)

token_auth_scheme = HTTPBearer()
key_service = KeyService()
authorize = Authorize()


@router.get("")
def get_keys(token: str = Depends(token_auth_scheme)) -> List[KeyPreviewResponse]:
    org_id = authorize.user(VerifyToken(token.credentials).verify()).organization_id
    return key_service.get_keys(org_id)


@router.post("", status_code=status.HTTP_201_CREATED)
async def add_key(
    key_request: KeyGenerationRequest, token: str = Depends(token_auth_scheme)
) -> KeyResponse:
    org_id = authorize.user(VerifyToken(token.credentials).verify()).organization_id
    return key_service.add_key(key_request, org_id)


@router.delete("/{id}")
async def revoke_key(id: ObjectIdString, token: str = Depends(token_auth_scheme)):
    org_id = authorize.user(VerifyToken(token.credentials).verify()).organization_id
    return key_service.revoke_key(id, org_id)
