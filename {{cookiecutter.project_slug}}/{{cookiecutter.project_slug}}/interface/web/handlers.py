from fastapi import Request
from fastapi.responses import JSONResponse

from {{ cookiecutter.project_slug }}.domain.errors import DomainError

DOMAIN_ERROR_STATUS_MAP: dict[type[DomainError], int] = {}


async def domain_error_handler(_request: Request, exc: DomainError) -> JSONResponse:
    status = DOMAIN_ERROR_STATUS_MAP.get(type(exc), 400)
    return JSONResponse(
        status_code=status,
        content={"detail": str(exc), "error_type": type(exc).__name__},
    )
