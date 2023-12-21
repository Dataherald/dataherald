from fastapi import APIRouter, Depends, Security, status
from fastapi.security import HTTPBearer

from modules.finetuning.models.requests import FinetuningRequest
from modules.finetuning.models.responses import FinetuningResponse
from modules.finetuning.service import FinetuningService
from utils.auth import Authorize, VerifyToken, get_api_key

router = APIRouter(
    prefix="/finetunings",
    responses={404: {"description": "Not found"}},
)

api_router = APIRouter(
    prefix="/api/finetunings",
    responses={404: {"description": "Not found"}},
)

token_auth_scheme = HTTPBearer()
authorize = Authorize()
finetuning_service = FinetuningService()


@router.get("/{id}")
async def get_finetuning_job(
    id: str, token: str = Depends(token_auth_scheme)
) -> FinetuningResponse:
    user = authorize.user(VerifyToken(token.credentials).verify())
    return await finetuning_service.get_finetuning_job(id, user.organization_id)


@api_router.get("/{id}")
async def api_get_finetuning_job(
    id: str,
    api_key: str = Security(get_api_key),
) -> FinetuningResponse:
    return await finetuning_service.get_finetuning_job(id, api_key.organization_id)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_finetuning_job(
    finetuning_request: FinetuningRequest,
    token: str = Depends(token_auth_scheme),
) -> FinetuningResponse:
    user = authorize.user(VerifyToken(token.credentials).verify())
    return await finetuning_service.create_finetuning_job(
        finetuning_request, user.organization_id
    )


@api_router.post("", status_code=status.HTTP_201_CREATED)
async def api_create_api_finetuning_job(
    finetuning_request: FinetuningRequest,
    api_key: str = Security(get_api_key),
) -> FinetuningResponse:
    return await finetuning_service.create_finetuning_job(
        finetuning_request, api_key.organization_id
    )


@router.post("/{id}/cancel")
async def cancel_finetuning_job(
    id: str,
    token: str = Depends(token_auth_scheme),
) -> FinetuningResponse:
    user = authorize.user(VerifyToken(token.credentials).verify())
    return await finetuning_service.cancel_finetuning_job(id, user.organization_id)


@api_router.post("/{id}/cancel")
async def api_cancel_finetuning_job(
    id: str,
    api_key: str = Security(get_api_key),
) -> FinetuningResponse:
    return await finetuning_service.cancel_finetuning_job(id, api_key.organization_id)
