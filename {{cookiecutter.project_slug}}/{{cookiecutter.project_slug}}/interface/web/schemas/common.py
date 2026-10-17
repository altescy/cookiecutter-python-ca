from pydantic import BaseModel


class ErrorResponse(BaseModel):
    detail: str
    error_type: str


class PaginatedResponse[T](BaseModel):
    items: list[T]
    total: int
    offset: int
    limit: int
