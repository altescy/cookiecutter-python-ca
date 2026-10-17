"""Run make targets in generated projects and verify they complete successfully."""

import os
import shutil
import subprocess
from pathlib import Path

import pytest

BUN_AVAILABLE = shutil.which("bun") is not None


def make(project: Path, *targets: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["make", *targets],
        cwd=project,
        capture_output=True,
        text=True,
    )


def assert_success(result: subprocess.CompletedProcess[str]) -> None:
    assert result.returncode == 0, (
        f"Command failed (exit {result.returncode})\n"
        f"--- stdout ---\n{result.stdout}\n"
        f"--- stderr ---\n{result.stderr}"
    )


class TestMakeMinimal:
    """use_web_api=no, use_frontend=no — make all must pass."""

    @pytest.fixture
    def project(self, bake: object) -> Path:
        return bake(use_web_api="no", use_frontend="no")  # type: ignore[operator]

    def test_format_python(self, project: Path) -> None:
        assert_success(make(project, "format-python"))

    def test_lint_python(self, project: Path) -> None:
        assert_success(make(project, "lint-python"))

    def test_test_python(self, project: Path) -> None:
        assert_success(make(project, "test-python"))

    def test_make_all(self, project: Path) -> None:
        assert_success(make(project, "all"))


class TestMakeWebAPI:
    """use_web_api=yes, use_frontend=no — make all must pass."""

    @pytest.fixture
    def project(self, bake: object) -> Path:
        return bake(use_web_api="yes", use_frontend="no")  # type: ignore[operator]

    def test_format_python(self, project: Path) -> None:
        assert_success(make(project, "format-python"))

    def test_lint_python(self, project: Path) -> None:
        assert_success(make(project, "lint-python"))

    def test_test_python(self, project: Path) -> None:
        assert_success(make(project, "test-python"))

    def test_make_all(self, project: Path) -> None:
        assert_success(make(project, "all"))


@pytest.mark.skipif(not BUN_AVAILABLE, reason="bun is not available")
class TestMakeFullStack:
    """use_web_api=yes, use_frontend=yes — make all must pass (requires bun)."""

    @pytest.fixture
    def project(self, bake: object) -> Path:
        p: Path = bake(use_web_api="yes", use_frontend="yes")  # type: ignore[operator]
        result = subprocess.run(
            ["bun", "install"],
            cwd=p / "web",
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"bun install failed:\n{result.stderr}"
        return p

    def test_format_python(self, project: Path) -> None:
        assert_success(make(project, "format-python"))

    def test_lint_python(self, project: Path) -> None:
        assert_success(make(project, "lint-python"))

    def test_test_python(self, project: Path) -> None:
        assert_success(make(project, "test-python"))

    def test_make_all(self, project: Path) -> None:
        assert_success(make(project, "all"))

    def test_frontend_build(self, project: Path) -> None:
        assert_success(make(project, "frontend"))

    def test_lint_typescript(self, project: Path) -> None:
        assert_success(make(project, "lint-typescript"))

    def test_generated_api_checks_and_build(self, project: Path) -> None:
        assert_success(make(project, "generate-api"))
        generated = project / "web/src/shared/api/generated"
        assert (generated / "sdk.gen.ts").is_file()
        assert (generated / "types.gen.ts").is_file()
        api = project / "web/src/shared/api/index.ts"
        api.write_text('export { createClient, createConfig } from "./generated/client";\n')
        assert_success(make(project, "lint-typescript", "frontend"))

    def test_architecture(self, project: Path) -> None:
        result = subprocess.run(
            ["bun", "run", "lint:architecture"], cwd=project / "web", capture_output=True, text=True
        )
        assert_success(result)

    @pytest.mark.parametrize(
        ("target", "rule"),
        [
            ("@/app/App", "fsd/forbidden-imports"),
            ("../../../app/App", "fsd/forbidden-imports"),
            ("@/pages/other", "fsd/forbidden-imports"),
            ("../../other", "fsd/forbidden-imports"),
            ("@/shared/api/internal", "fsd/no-public-api-sidestep"),
            ("../../../shared/api/internal", "fsd/no-public-api-sidestep"),
            ("@/shared/api/generated/client", "fsd/no-public-api-sidestep"),
        ],
    )
    def test_architecture_rejects_invalid_imports(self, project: Path, target: str, rule: str) -> None:
        src = project / "web/src"
        other = src / "pages/other"
        (other / "ui").mkdir(parents=True)
        (other / "ui/other-page.tsx").write_text("export const OtherPage = () => null;\n")
        (other / "index.ts").write_text('export { OtherPage } from "./ui/other-page";\n')
        (src / "shared/api/internal.ts").write_text("export const internal = true;\n")
        generated = src / "shared/api/generated"
        generated.mkdir()
        (generated / "client.ts").write_text("export const generated = true;\n")
        page = src / "pages/home/ui/home-page.tsx"
        page.write_text(f'import * as forbidden from "{target}";\n' + page.read_text() + "\nvoid forbidden;\n")

        result = subprocess.run(
            ["bun", "run", "lint:architecture"], cwd=project / "web", capture_output=True, text=True
        )
        assert result.returncode != 0, result.stdout + result.stderr
        assert rule in result.stdout + result.stderr

    def test_architecture_ignores_generated_code(self, project: Path) -> None:
        generated = project / "web/src/shared/api/generated"
        generated.mkdir()
        (generated / "client.ts").write_text('export { App } from "@/app/App";\n')
        result = subprocess.run(
            ["bun", "run", "lint:architecture"], cwd=project / "web", capture_output=True, text=True
        )
        assert_success(result)


@pytest.mark.parametrize("python_version", ["3.12", "3.13", "3.14"])
def test_supported_python_versions(bake: object, python_version: str) -> None:
    project: Path = bake(  # type: ignore[operator]
        use_web_api="yes", use_frontend="no", python_version=python_version
    )
    result = subprocess.run(
        ["make", "all"],
        cwd=project,
        env={**os.environ, "UV_PYTHON": python_version},
        capture_output=True,
        text=True,
    )
    assert_success(result)
