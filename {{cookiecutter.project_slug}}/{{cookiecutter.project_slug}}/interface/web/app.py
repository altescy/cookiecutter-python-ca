from collections.abc import AsyncGenerator
from contextlib import aclosing, asynccontextmanager

from fastapi import FastAPI


def create_app() -> FastAPI:
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import FileResponse, HTMLResponse
    from fastapi.staticfiles import StaticFiles

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

    if STATIC_DIR.exists():
        app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets", html=True), name="ui")

        @app.get("/favicon.svg", response_class=FileResponse)
        def favicon() -> FileResponse:  # pyright: ignore[reportUnusedFunction]
            return FileResponse(STATIC_DIR / "favicon.svg", media_type="image/svg+xml")

        @app.get("/{full_path:path}", response_class=HTMLResponse)
        def spa_fallback(full_path: str) -> FileResponse:  # pyright: ignore[reportUnusedFunction]
            return FileResponse(STATIC_DIR / "index.html", media_type="text/html")

    return app
