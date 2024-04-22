import logging

from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

ERROR_MAPPING = {
    "InvalidId": "invalid_object_id",
    "InvalidDBConnectionError": "invalid_database_connection",
    "InvalidURIFormatError": "invalid_database_uri_format",
    "SSHInvalidDatabaseConnectionError": "ssh_invalid_database_connection",
    "EmptyDBError": "empty_database",
    "DatabaseConnectionNotFoundError": "database_connection_not_found",
    "GoldenSQLNotFoundError": "golden_sql_not_found",
    "LLMNotSupportedError": "llm_model_not_supported",
    "PromptNotFoundError": "prompt_not_found",
    "SQLGenerationError": "sql_generation_not_created",
    "SQLInjectionError": "sql_injection",
    "SQLGenerationNotFoundError": "sql_generation_not_found",
    "NLGenerationError": "nl_generation_not_created",
    "MalformedGoldenSQLError": "invalid_golden_sql",
    "SchemaNotSupportedError": "schema_not_supported",
}


class CustomError(Exception):
    def __init__(self, message, description=None):
        super().__init__(message)
        self.description = description


def error_response(error, detail: dict, default_error_code=""):
    error_code = ERROR_MAPPING.get(error.__class__.__name__, default_error_code)
    description = getattr(error, "description", None)
    logger.error(
        f"Error code: {error_code}, message: {error}, description: {description}, detail: {detail}"
    )

    detail.pop("metadata", None)

    return JSONResponse(
        status_code=400,
        content={
            "error_code": error_code,
            "message": str(error),
            "description": description,
            "detail": detail,
        },
    )


def stream_error_response(error, detail: dict, default_error_code=""):
    error_code = ERROR_MAPPING.get(error.__class__.__name__, default_error_code)
    description = getattr(error, "description", None)
    logger.error(
        f"Error code: {error_code}, message: {error}, description: {description}, detail: {detail}"
    )

    detail.pop("metadata", None)

    return {
        "error_code": error_code,
        "message": str(error),
        "description": description,
        "detail": detail,
    }
