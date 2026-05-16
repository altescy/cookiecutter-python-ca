# {{ cookiecutter.project_name }}

{{ cookiecutter.project_description }}

## Setup

```bash
uv sync --group dev
cp .env.example .env
```

## Development

```bash
make all       # format + lint + test
make format    # format code
make lint      # lint and type-check
make test      # run tests
{% if cookiecutter.use_web_api == "yes" %}make serve     # start development server{% endif %}
```

## Architecture

This project follows Clean Architecture with strict dependency rules:

```
{{ cookiecutter.project_slug }}/
├── domain/          # Core business logic — no external dependencies
│   ├── entities/    # Immutable domain objects
│   ├── repositories/  # Repository protocols (typing.Protocol)
│   ├── services/    # Pure domain services
│   ├── value_objects/
│   └── errors.py
├── application/     # Use cases — depends on domain only
│   └── usecases/
├── infrastructure/  # Implementations — depends on domain protocols
│   └── repositories/
├── interface/       # Delivery mechanisms
│   ├── cli/
{%- if cookiecutter.use_web_api == "yes" %}
│   └── web/         # FastAPI routes and schemas
{%- else %}
│   └── ...
{%- endif %}
└── bootstrap/       # Wiring: settings and DI container
```

**Dependency rule:** domain ← application ← infrastructure / interface ← bootstrap
