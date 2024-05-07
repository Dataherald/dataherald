from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)

from exceptions.error_codes import BaseErrorCode, ErrorCodeData
from exceptions.exceptions import BaseError


class InstructionErrorCode(BaseErrorCode):
    instruction_not_found = ErrorCodeData(
        status_code=HTTP_404_NOT_FOUND, message="Instruction not found"
    )
    single_instruction_only = ErrorCodeData(
        status_code=HTTP_400_BAD_REQUEST,
        message="Only one instruction allowed per database connection",
    )


class InstructionError(BaseError):
    """
    Base class for instruction exceptions
    """

    ERROR_CODES: BaseErrorCode = InstructionErrorCode


class InstructionNotFoundError(InstructionError):
    def __init__(
        self, org_id: str, instruction_id: str = None, db_connection_id: str = None
    ) -> None:
        if instruction_id:
            detail = {"instruction_id": instruction_id, "organization_id": org_id}
        elif db_connection_id:
            detail = {"db_connection_id": db_connection_id, "organization_id": org_id}
        else:
            raise ValueError("instruction_id or db_connection_id must be provided")
        super().__init__(
            error_code=InstructionErrorCode.instruction_not_found.name,
            detail=detail,
        )


class SingleInstructionOnlyError(InstructionError):
    def __init__(self, db_connection_id: str, org_id: str) -> None:
        super().__init__(
            error_code=InstructionErrorCode.single_instruction_only.name,
            detail={"db_connection_id": db_connection_id, "organization_id": org_id},
        )
