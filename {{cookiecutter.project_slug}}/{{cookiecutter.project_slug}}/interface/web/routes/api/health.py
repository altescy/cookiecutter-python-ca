from typing import Final

from fastapi import APIRouter

ROUTER: Final[APIRouter] = APIRouter()


@ROUTER.get("/health")
def health() -> str:
    return "OK"
