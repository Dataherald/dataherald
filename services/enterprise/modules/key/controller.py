from typing import List

from fastapi import APIRouter, Security, status

from modules.key.models.requests import KeyGenerationRequest
from modules.key.models.responses import KeyPreviewResponse, KeyResponse
from modules.key.service import KeyService
from utils.auth import User, authenticate_user
from utils.validation import ObjectIdString

router = APIRouter(
    prefix="/keys",
    responses={404: {"description": "Not found"}},
)

key_service = KeyService()


@router.get("")
def get_keys(user: User = Security(authenticate_user)) -> List[KeyPreviewResponse]:
    return key_service.get_keys(user.organization_id)


@router.post("", status_code=status.HTTP_201_CREATED)
async def add_key(
    key_request: KeyGenerationRequest, user: User = Security(authenticate_user)
) -> KeyResponse:
    return key_service.add_key(key_request, user.organization_id)


@router.delete("/{id}")
async def revoke_key(id: ObjectIdString, user: User = Security(authenticate_user)):
    return key_service.revoke_key(id, user.organization_id)
