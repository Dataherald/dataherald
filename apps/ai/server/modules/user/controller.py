from fastapi import APIRouter

router = APIRouter(prefix="/user", responses={404: {"description": "Not found"}})
