import logging

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class GenerationEngineError(Exception):
    def __init__(
        self, status_code: int, prompt_id: str, display_id: str, error_message: str
    ):
        self.status_code = status_code
        self.prompt_id = prompt_id
        self.display_id = display_id
        self.error_message = error_message


async def query_engine_exception_handler(
    request: Request, exc: GenerationEngineError  # noqa: ARG001
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "prompt_id": exc.prompt_id,
            "display_id": exc.display_id,
            "error_message": exc.error_message,
        },
    )


def raise_for_status(status_code: int, message: str = None):
    if status_code < status.HTTP_400_BAD_REQUEST:
        return

    logger.error("Error from K2-Engine: %s", message)
    raise HTTPException(
        status_code=status_code, detail=f"Error from K2-Engine: {message}"
    )
