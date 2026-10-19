from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from {{ cookiecutter.project_slug }}.interface.web import constants
from {{ cookiecutter.project_slug }}.interface.web.app import create_app


@pytest.fixture
def static_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(constants, "STATIC_DIR", tmp_path)
    (tmp_path / "index.html").write_text("<!doctype html><html><body>Frontend</body></html>")
    (tmp_path / "favicon.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
    (tmp_path / "robots.txt").write_text("User-agent: *\nDisallow:\n")
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets/app.js").write_text('console.log("frontend");')
    (tmp_path / "api").mkdir()
    (tmp_path / "api/health").write_text("Not the API response")
    return tmp_path


@pytest.fixture
def frontend_client(static_dir: Path) -> Iterator[TestClient]:
    with TestClient(create_app()) as client:
        yield client


@pytest.mark.parametrize("path", ["/", "/index.html", "/dashboard/settings"])
def test_serves_frontend(frontend_client: TestClient, static_dir: Path, path: str) -> None:
    response = frontend_client.get(path, headers={"Accept": "text/html"})
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert response.text == (static_dir / "index.html").read_text()


@pytest.mark.parametrize("path", ["/assets/app.js", "/favicon.svg", "/robots.txt"])
def test_serves_static_files(frontend_client: TestClient, static_dir: Path, path: str) -> None:
    response = frontend_client.get(path)
    assert response.status_code == 200
    assert response.content == (static_dir / path.lstrip("/")).read_bytes()


@pytest.mark.parametrize("accept", ["application/json", "*/*"])
def test_spa_fallback_requires_html_accept(frontend_client: TestClient, accept: str) -> None:
    response = frontend_client.get("/dashboard/settings", headers={"Accept": accept})
    assert response.status_code == 404


@pytest.mark.parametrize(
    ("path", "accept"),
    [("/assets/missing.js", "*/*"), ("/missing.css", "text/css,*/*;q=0.1"), ("/missing.png", "image/png,*/*;q=0.8")],
)
def test_missing_assets_do_not_use_spa_fallback(frontend_client: TestClient, path: str, accept: str) -> None:
    response = frontend_client.get(path, headers={"Accept": accept})
    assert response.status_code == 404


def test_head_supports_spa_navigation(frontend_client: TestClient) -> None:
    response = frontend_client.head("/dashboard/settings", headers={"Accept": "text/html"})
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert response.content == b""


@pytest.mark.parametrize("method", ["POST", "PUT", "DELETE"])
def test_spa_fallback_rejects_other_methods(frontend_client: TestClient, method: str) -> None:
    response = frontend_client.request(method, "/dashboard/settings", headers={"Accept": "text/html"})
    assert response.status_code == 404


def test_api_routes_take_priority(frontend_client: TestClient) -> None:
    response = frontend_client.get("/api/health", headers={"Accept": "text/html"})
    assert response.status_code == 200
    assert response.json() == "OK"


def test_routes_added_after_frontend_take_priority(static_dir: Path) -> None:
    app = create_app()

    def late_route() -> str:
        return "API response"

    app.add_api_route("/dashboard/settings", late_route)
    with TestClient(app) as client:
        response = client.get("/dashboard/settings", headers={"Accept": "text/html"})
        assert response.status_code == 200
        assert response.json() == "API response"


def test_api_not_found_stays_json(frontend_client: TestClient) -> None:
    response = frontend_client.get("/api/missing", headers={"Accept": "application/json"})
    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/json")


def test_frontend_is_not_in_openapi(frontend_client: TestClient) -> None:
    response = frontend_client.get("/openapi.json")
    assert response.status_code == 200
    assert set(response.json()["paths"]) == {"/api/health"}
    assert frontend_client.get("/docs").status_code == 200


def test_frontend_without_assets_directory(static_dir: Path) -> None:
    (static_dir / "assets/app.js").unlink()
    (static_dir / "assets").rmdir()
    with TestClient(create_app()) as client:
        assert client.get("/").status_code == 200


def test_backend_starts_without_frontend_build(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(constants, "STATIC_DIR", tmp_path / "missing-build")
    with TestClient(create_app()) as client:
        assert client.get("/api/health").status_code == 200
        assert client.get("/", headers={"Accept": "text/html"}).status_code == 404
