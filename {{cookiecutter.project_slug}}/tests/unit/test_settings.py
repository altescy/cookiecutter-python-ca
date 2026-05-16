from {{ cookiecutter.project_slug }}.bootstrap.settings import AppSettings


class TestSettings:
    def test_default_values(self) -> None:
        settings = AppSettings()
        assert settings.debug is False
