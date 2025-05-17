from typing import List, TypeVar, Generic
from pydantic.generics import GenericModel

T = TypeVar('T')

class PaginatedResponse(GenericModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int
    pages: int

def paginate(items: List[T], page: int, size: int) -> PaginatedResponse[T]:
    total = len(items)
    pages = (total + size - 1) // size
    start = (page - 1) * size
    end = start + size
    return PaginatedResponse(
        items=items[start:end],
        total=total,
        page=page,
        size=size,
        pages=pages
    )
