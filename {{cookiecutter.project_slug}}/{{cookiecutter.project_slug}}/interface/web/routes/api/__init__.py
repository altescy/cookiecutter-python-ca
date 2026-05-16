from typing import Final

from fastapi import APIRouter

from . import health

ROUTER: Final[APIRouter] = APIRouter()
ROUTER.include_router(health.ROUTER)
