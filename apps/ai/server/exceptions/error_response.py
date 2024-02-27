from pydantic import BaseModel


class ErrorResponse(BaseModel):
    trace_id: str
    error_code: str
    message: str
    detail: dict | None = None
