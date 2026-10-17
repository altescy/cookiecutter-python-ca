"""Verify generated file structure for each option combination."""

from pathlib import Path

import pytest


SLUG = "test_app"

# Files present in every generated project
ALWAYS_PRESENT = [
    "pyproject.toml",
    "Makefile",
    ".gitignore",
    ".env.example",
    "README.md",
    "AGENTS.md",
    "docs/DEVELOPMENT_GUIDELINES.md",
    f"{SLUG}/__init__.py",
    f"{SLUG}/domain/__init__.py",
    f"{SLUG}/domain/errors.py",
    f"{SLUG}/domain/entities/__init__.py",
    f"{SLUG}/domain/repositories/__init__.py",
    f"{SLUG}/domain/services/__init__.py",
    f"{SLUG}/domain/value_objects/__init__.py",
    f"{SLUG}/application/__init__.py",
    f"{SLUG}/application/usecases/__init__.py",
    f"{SLUG}/infrastructure/__init__.py",
    f"{SLUG}/infrastructure/repositories/__init__.py",
    f"{SLUG}/interface/__init__.py",
    f"{SLUG}/interface/cli/__init__.py",
    f"{SLUG}/interface/cli/app.py",
    f"{SLUG}/bootstrap/__init__.py",
    f"{SLUG}/bootstrap/settings.py",
    f"{SLUG}/bootstrap/container.py",
    "tests/__init__.py",
    "tests/unit/__init__.py",
    "tests/unit/test_settings.py",
    "tests/unit/domain/__init__.py",
    "tests/unit/domain/entities/__init__.py",
    "tests/unit/application/__init__.py",
    "tests/unit/application/usecases/__init__.py",
    "tests/unit/infrastructure/__init__.py",
    "tests/unit/infrastructure/repositories/__init__.py",
    "tests/integration/__init__.py",
]

# Files only present when use_web_api=yes
WEB_ONLY = [
    f"{SLUG}/interface/web/__init__.py",
    f"{SLUG}/interface/web/app.py",
    f"{SLUG}/interface/web/constants.py",
    f"{SLUG}/interface/web/dependencies.py",
    f"{SLUG}/interface/web/handlers.py",
    f"{SLUG}/interface/web/routes/__init__.py",
    f"{SLUG}/interface/web/routes/api/__init__.py",
    f"{SLUG}/interface/web/routes/api/health.py",
    f"{SLUG}/interface/web/schemas/__init__.py",
    f"{SLUG}/interface/web/schemas/common.py",
    "tests/integration/conftest.py",
    "tests/integration/web/__init__.py",
    "tests/integration/web/test_health.py",
]

# Files only present when use_frontend=yes (requires use_web_api=yes)
FRONTEND_ONLY = [
    "web/package.json",
    "web/tsconfig.json",
    "web/vite.config.ts",
    "web/biome.json",
    "web/steiger.config.ts",
    "web/openapi-ts.config.ts",
    "web/index.html",
    "web/public/favicon.svg",
    "web/src/main.tsx",
    "web/src/app/App.tsx",
    "web/src/app/styles/index.css",
    "web/src/pages/home/index.ts",
    "web/src/pages/home/ui/home-page.tsx",
    "web/src/shared/api/index.ts",
    "web/src/vite-env.d.ts",
]


def assert_files_exist(project: Path, files: list[str]) -> None:
    for f in files:
        assert (project / f).exists(), f"Expected file missing: {f}"


def assert_files_absent(project: Path, files: list[str]) -> None:
    for f in files:
        assert not (project / f).exists(), f"Unexpected file present: {f}"


class TestMinimal:
    """use_web_api=no, use_frontend=no"""

    @pytest.fixture
    def project(self, bake: object) -> Path:
        return bake(use_web_api="no", use_frontend="no")  # type: ignore[operator]

    def test_always_present_files_exist(self, project: Path) -> None:
        assert_files_exist(project, ALWAYS_PRESENT)

    def test_web_files_absent(self, project: Path) -> None:
        assert_files_absent(project, WEB_ONLY)

    def test_frontend_absent(self, project: Path) -> None:
        assert not (project / "web").exists()

    def test_pyproject_has_pydantic(self, project: Path) -> None:
        content = (project / "pyproject.toml").read_text()
        assert "pydantic>=" in content
        assert "pydantic-settings>=" in content

    def test_pyproject_no_fastapi(self, project: Path) -> None:
        content = (project / "pyproject.toml").read_text()
        assert "fastapi" not in content
        assert "uvicorn" not in content
        assert "httpx" not in content

    def test_makefile_no_serve(self, project: Path) -> None:
        content = (project / "Makefile").read_text()
        assert "serve" not in content

    def test_makefile_no_frontend_targets(self, project: Path) -> None:
        content = (project / "Makefile").read_text()
        assert "frontend" not in content
        assert "generate-api" not in content

    def test_settings_env_prefix(self, project: Path) -> None:
        content = (project / SLUG / "bootstrap" / "settings.py").read_text()
        assert '"test_app_"' in content


class TestWebAPI:
    """use_web_api=yes, use_frontend=no"""

    @pytest.fixture
    def project(self, bake: object) -> Path:
        return bake(use_web_api="yes", use_frontend="no")  # type: ignore[operator]

    def test_always_present_files_exist(self, project: Path) -> None:
        assert_files_exist(project, ALWAYS_PRESENT)

    def test_web_files_exist(self, project: Path) -> None:
        assert_files_exist(project, WEB_ONLY)

    def test_frontend_absent(self, project: Path) -> None:
        assert not (project / "web").exists()

    def test_pyproject_has_fastapi(self, project: Path) -> None:
        content = (project / "pyproject.toml").read_text()
        assert "fastapi" in content
        assert "uvicorn" in content
        assert "httpx" in content

    def test_makefile_has_serve(self, project: Path) -> None:
        content = (project / "Makefile").read_text()
        assert "serve" in content

    def test_makefile_no_frontend_targets(self, project: Path) -> None:
        content = (project / "Makefile").read_text()
        assert "frontend" not in content
        assert "generate-api" not in content


class TestFullStack:
    """use_web_api=yes, use_frontend=yes"""

    @pytest.fixture
    def project(self, bake: object) -> Path:
        return bake(use_web_api="yes", use_frontend="yes")  # type: ignore[operator]

    def test_always_present_files_exist(self, project: Path) -> None:
        assert_files_exist(project, ALWAYS_PRESENT)

    def test_web_files_exist(self, project: Path) -> None:
        assert_files_exist(project, WEB_ONLY)

    def test_frontend_files_exist(self, project: Path) -> None:
        assert_files_exist(project, FRONTEND_ONLY)

    def test_frontend_starts_with_minimal_fsd_layers(self, project: Path) -> None:
        src = project / "web" / "src"
        assert not (src / "App.tsx").exists()
        for layer in ("widgets", "features", "entities"):
            assert not (src / layer).exists()

    def test_home_page_project_name(self, project: Path) -> None:
        content = (project / "web/src/pages/home/ui/home-page.tsx").read_text()
        assert "test app" in content

    def test_makefile_has_all_targets(self, project: Path) -> None:
        content = (project / "Makefile").read_text()
        assert "serve" in content
        assert "frontend" in content
        assert "generate-api" in content
        assert "format-typescript" in content
        assert "lint-typescript" in content
        assert "test-typescript" in content

    def test_frontend_project_name(self, project: Path) -> None:
        content = (project / "web" / "index.html").read_text()
        assert "test app" in content
