import uuid

from starlette.status import HTTP_400_BAD_REQUEST


def is_http_error(status_code: int) -> bool:
    return status_code >= HTTP_400_BAD_REQUEST


def generate_trace_id():
    return f"E-{str(uuid.uuid4())}"  # Generate a unique trace ID for each error
