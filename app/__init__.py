from typing import Optional, Type, TypeVar, Generic, List
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)


class PaginatedResponse(BaseModel, Generic[T]):
    count: int
    next: Optional[str]
    previous: Optional[str]
    results: List[T]
