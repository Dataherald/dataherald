from abc import ABC

from exceptions.error_codes import BaseErrorCode, GeneralErrorCode
from exceptions.utils import generate_trace_id


class BaseError(ABC, Exception):
    ERROR_CODES: BaseErrorCode = None

    @property
    def trace_id(self) -> str:
        return self._trace_id

    @property
    def error_code(self) -> str:
        return self._error_code

    @property
    def status_code(self) -> str:
        return self._status_code

    @property
    def message(self) -> str:
        return self._message

    @property
    def description(self) -> str:
        return self._description

    @property
    def detail(self) -> dict:
        return self._detail

    def __init__(
        self,
        error_code: str = None,
        status_code: int = None,
        message: str = None,
        description: str = None,
        detail: dict = None,
    ) -> None:
        if type(self) is BaseError:
            raise TypeError("BaseError class may not be instantiated directly")

        if self.ERROR_CODES is None or not hasattr(self.ERROR_CODES, "__members__"):
            raise TypeError(
                f"ERROR_CODES in {self.__class__.__name__} must be defined and be an enum type"
            )

        def handled_error_code(error_code: str) -> bool:
            return error_code in self.ERROR_CODES.__members__

        self._trace_id = generate_trace_id()

        if error_code is not None:
            self._error_code = error_code

            if handled_error_code(error_code):
                self._status_code = self.ERROR_CODES[error_code].value.status_code
                self._message = (
                    message
                    if message is not None
                    else self.ERROR_CODES[error_code].value.message
                )
            else:
                self._status_code = status_code if status_code is not None else 500
                self._message = (
                    message
                    if message is not None
                    else f"Unknown error_code: {error_code}"
                )
        else:
            self._status_code = status_code if status_code is not None else 500
            self._message = message if message is not None else "Unknown error"

        self._detail = detail if detail is not None else {}
        self._description = description


class GeneralError(BaseError):
    """
    Base class for general exceptions
    """

    ERROR_CODES: BaseErrorCode = GeneralErrorCode


class EngineError(GeneralError):
    def __init__(
        self,
        error_code: str,
        status_code: int,
        message: str,
        description: str,
        detail: dict,
    ) -> None:
        super().__init__(
            error_code=error_code,
            status_code=status_code,
            message=message,
            description=description,
            detail=detail,
        )


class UnhandledEngineError(GeneralError):
    def __init__(self) -> None:
        super().__init__(
            error_code=GeneralErrorCode.unhandled_engine_error.name,
        )


class ReservedMetadataKeyError(GeneralError):
    def __init__(self) -> None:
        super().__init__(
            error_code=GeneralErrorCode.reserved_metadata_key.name,
        )


class UnknownError(GeneralError):
    def __init__(self, error: str = None) -> None:
        super().__init__(
            error_code=GeneralErrorCode.unknown_error.name, description=error
        )
