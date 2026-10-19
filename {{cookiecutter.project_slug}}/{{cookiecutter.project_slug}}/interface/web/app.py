from collections.abc import AsyncGenerator
from contextlib import aclosing, asynccontextmanager

from fastapi import FastAPI


def create_app() -> FastAPI:
    from fastapi.middleware.cors import CORSMiddleware

    from {{ cookiecutter.project_slug }}.domain.errors import DomainError

    from .constants import STATIC_DIR
    from .dependencies import get_container
    from .handlers import domain_error_handler
    from .routes import api

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncGenerator[None]:
        container = get_container()
        async with aclosing(container):
            yield

    app = FastAPI(lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_exception_handler(DomainError, domain_error_handler)  # type: ignore[arg-type]

    app.include_router(api.ROUTER, prefix="/api")

    if STATIC_DIR.is_dir():
        app.frontend("/", directory=STATIC_DIR, fallback="index.html")

    return app
