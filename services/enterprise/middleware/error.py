from fastapi import Request
from fastapi.logger import logger
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from exceptions.error_codes import GeneralErrorCode
from exceptions.error_response import ErrorResponse
from exceptions.utils import generate_trace_id


class UnknownErrorMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception:
            trace_id = generate_trace_id()
            logger.error(f"Unhandled ERROR\nTrace ID: {trace_id}", exc_info=True)

            error_code = GeneralErrorCode.unknown_error.name
            status_code = GeneralErrorCode.unknown_error.value.status_code
            message = GeneralErrorCode.unknown_error.value.message

            # raising an exception here causes problems with the exception handling
            return JSONResponse(
                status_code=status_code,
                content=ErrorResponse(
                    trace_id=trace_id,
                    error_code=error_code,
                    message=message,
                ).dict(),
            )
