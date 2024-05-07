from enum import Enum, EnumMeta

from pydantic import BaseModel
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR,
)


class ErrorCodeData(BaseModel):
    status_code: int
    message: str


class ErrorCodeInterface(EnumMeta):
    def __new__(cls, metacls, bases, classdict):
        enum_class = super().__new__(cls, metacls, bases, classdict)
        for name, member in enum_class.__members__.items():
            if not isinstance(member.value, ErrorCodeData):
                raise TypeError(
                    f"Enum value for {name} must be an instance of ErrorCodeData"
                )
        return enum_class


class BaseErrorCode(Enum, metaclass=ErrorCodeInterface):
    """ ""
    This class serves as a base for all Error code enums
    It will enforce that all enum values are instances of ErrorCodeData
    """

    pass


class GeneralErrorCode(BaseErrorCode):
    unknown_error = ErrorCodeData(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR, message="Unknown error"
    )
    unhandled_engine_error = ErrorCodeData(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR, message="Unhandled engine error"
    )
    reserved_metadata_key = ErrorCodeData(
        status_code=HTTP_400_BAD_REQUEST, message="Metadata cannot contain reserved key"
    )
