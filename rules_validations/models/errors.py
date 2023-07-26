from dataclasses import dataclass


@dataclass
class ErrorWrapper(BaseException):
    key: str
    exception: Exception


ValidationError = BaseExceptionGroup
