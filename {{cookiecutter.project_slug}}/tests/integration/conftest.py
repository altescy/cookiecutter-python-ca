from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from {{ cookiecutter.project_slug }}.bootstrap.container import Container
from {{ cookiecutter.project_slug }}.bootstrap.settings import AppSettings
from {{ cookiecutter.project_slug }}.interface.web.app import create_app
from {{ cookiecutter.project_slug }}.interface.web.dependencies import get_container, get_settings


@pytest.fixture
def client() -> Iterator[TestClient]:
    settings = AppSettings()

    def override_settings() -> AppSettings:
        return settings

    container = Container(settings)

    def override_container() -> Container:
        return container

    app = create_app()
    app.dependency_overrides[get_settings] = override_settings
    app.dependency_overrides[get_container] = override_container

    with TestClient(app) as tc:
        yield tc
