from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)

from exceptions.error_codes import BaseErrorCode, ErrorCodeData
from exceptions.exceptions import BaseError


class GenerationErrorCode(BaseErrorCode):
    prompt_not_found = ErrorCodeData(
        status_code=HTTP_404_NOT_FOUND, message="Prompt not found"
    )
    sql_generation_not_found = ErrorCodeData(
        status_code=HTTP_404_NOT_FOUND, message="SQL generation not found"
    )
    nl_generation_not_found = ErrorCodeData(
        status_code=HTTP_404_NOT_FOUND, message="NL generation not found"
    )
    generation_verified_or_rejected = ErrorCodeData(
        status_code=HTTP_400_BAD_REQUEST,
        message="Cannot modify verified or rejected generation",
    )
    invalid_sql_generation = ErrorCodeData(
        status_code=HTTP_400_BAD_REQUEST, message="Invalid SQL generation"
    )


class GenerationError(BaseError):
    """
    Base class for generation exceptions
    """

    ERROR_CODES: BaseErrorCode = GenerationErrorCode


class PromptNotFoundError(GenerationError):
    def __init__(self, prompt_id: str, org_id: str) -> None:
        super().__init__(
            error_code=GenerationErrorCode.prompt_not_found.name,
            detail={"prompt_id": prompt_id, "organization_id": org_id},
        )


class SqlGenerationNotFoundError(GenerationError):
    def __init__(self, sql_generation_id: str, org_id: str) -> None:
        super().__init__(
            error_code=GenerationErrorCode.sql_generation_not_found.name,
            detail={"sql_generation_id": sql_generation_id, "organization_id": org_id},
        )


class NlGenerationNotFoundError(GenerationError):
    def __init__(self, nl_generation_id: str, org_id: str) -> None:
        super().__init__(
            error_code=GenerationErrorCode.nl_generation_not_found.name,
            detail={"nl_generation_id": nl_generation_id, "organization_id": org_id},
        )


class GenerationVerifiedOrRejectedError(GenerationError):
    def __init__(self, nl_generation_id: str, org_id: str) -> None:
        super().__init__(
            error_code=GenerationErrorCode.generation_verified_or_rejected.name,
            detail={"nl_generation_id": nl_generation_id, "organization_id": org_id},
        )


class InvalidSqlGenerationError(GenerationError):
    def __init__(self, sql_generation_id: str, org_id: str) -> None:
        super().__init__(
            error_code=GenerationErrorCode.invalid_sql_generation.name,
            detail={"sql_generation_id": sql_generation_id, "organization_id": org_id},
        )
