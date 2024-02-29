from pydantic import BaseModel


class ErrorResponse(BaseModel):
    trace_id: str
    error_code: str
    message: str
    description: str | None = None
    detail: dict | None = None
