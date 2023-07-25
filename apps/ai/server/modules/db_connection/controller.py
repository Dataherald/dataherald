from fastapi import APIRouter

router = APIRouter(prefix="/databases", responses={404: {"description": "Not found"}})
