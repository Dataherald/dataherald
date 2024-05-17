from fastapi import Request
from fastapi.logger import logger
from fastapi.responses import JSONResponse
from httpx import Response

from exceptions.error_response import ErrorResponse
from exceptions.exceptions import (
    BaseError,
    EngineError,
    UnhandledEngineError,
)
from exceptions.utils import is_http_error


async def exception_handler(request: Request, exc: BaseError):  # noqa: ARG001
    trace_id = exc.trace_id
    error_code = exc.error_code
    status_code = exc.status_code
    message = exc.message
    description = exc.description
    detail = {k: v for k, v in exc.detail.items() if v is not None}

    logger.error(
        "ERROR\nTrace ID: %s, error_code: %s, detail: %s",
        trace_id,
        error_code,
        detail,
    )
    return JSONResponse(
        status_code=status_code,
        content=ErrorResponse(
            trace_id=trace_id,
            error_code=error_code,
            message=message,
            description=description,
            detail=detail,
        ).dict(),
    )


def raise_engine_exception(response: Response, org_id: str):
    if not is_http_error(response.status_code):
        return

    response_json: dict = response.json()

    if "error_code" in response_json:
        error_code = response_json["error_code"]
        message = response_json.get(
            "message", f"Unknown translation engine error_code: {error_code}"
        )
        description = response_json.get("description", None)
        detail = response_json.get("detail", {})
        detail["organization_id"] = org_id

        logger.error("Handled error from translation engine: %s", message)

        raise EngineError(
            error_code=error_code,
            status_code=response.status_code,
            message=message,
            description=description,
            detail=detail,
        )

    logger.error("Unhandled error from translation engine: %s", response.text)
    raise UnhandledEngineError()
