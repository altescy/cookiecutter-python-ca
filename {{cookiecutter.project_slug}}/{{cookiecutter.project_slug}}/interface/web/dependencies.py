from functools import cache

from {{ cookiecutter.project_slug }}.bootstrap.container import Container
from {{ cookiecutter.project_slug }}.bootstrap.settings import AppSettings


@cache
def get_settings() -> AppSettings:
    return AppSettings()


@cache
def get_container() -> Container:
    return Container(get_settings())
