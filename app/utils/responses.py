from typing import Any, Optional, TypeVar, Generic
from pydantic.generics import GenericModel

T = TypeVar('T')

class StandardResponse(GenericModel, Generic[T]):
    success: bool
    message: str
    data: Optional[T] = None

    @classmethod
    def ok(cls, data: Optional[T] = None, message: str = "Success"):
        return cls(success=True, message=message, data=data)

    @classmethod
    def error(cls, message: str = "Error", data: Optional[T] = None):
        return cls(success=False, message=message, data=data)
