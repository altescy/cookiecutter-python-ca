from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    model_config = {
        "env_prefix": "{{ cookiecutter.project_slug }}_",
        "env_nested_delimiter": "__",
    }

    debug: bool = False
