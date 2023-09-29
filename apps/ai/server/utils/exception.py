import logging

from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


def raise_for_status(status_code: int, message: str = None):
    if status_code < status.HTTP_400_BAD_REQUEST:
        return

    logger.error("Error from K2-Engine: %s", message)
    raise HTTPException(
        status_code=status_code, detail=f"Error from K2-Engine: {message}"
    )
