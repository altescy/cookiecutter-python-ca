# AGENTS.md

## Development Guidelines

**Read `docs/DEVELOPMENT_GUIDELINES.md` before making any changes.** It defines:

- Clean Architecture dependency rules (which layers can import what)
- Type safety requirements (pyright strict, no implicit any)
- Testing structure and conventions
- Code language policy (all code, comments, and docs in English)
{%- if cookiecutter.use_frontend == "yes" %}
- Frontend import rules (Feature-Sliced Design)
{%- endif %}

Violations of the dependency rule or type safety requirements must be fixed immediately.

## Commands

All commands run from the project root. Python managed by `uv`{% if cookiecutter.use_frontend == "yes" %}, frontend by `bun`{% endif %}.

```bash
# Full check (format → lint → test)
make all

# Python
make format-python      # ruff fix imports + format
make lint-python        # ruff check + pyright
make test-python        # pytest tests/
{%- if cookiecutter.use_frontend == "yes" %}

# TypeScript (runs inside web/)
make format-typescript  # biome format
make lint-typescript    # biome lint
make test-typescript    # vitest run
{%- endif %}
{%- if cookiecutter.use_web_api == "yes" %}

# Dev server
make serve              # uvicorn on :8000 (--reload)
{%- if cookiecutter.use_frontend == "yes" %}
cd web && bun run dev   # vite on :5173, proxies /api to :8000
{%- endif %}
{%- if cookiecutter.use_frontend == "yes" %}

# API client codegen (regenerate after changing FastAPI routes)
make generate-api
{%- endif %}
{%- endif %}
```

## Architecture

Clean Architecture layers under `{{ cookiecutter.project_slug }}/`:

| Layer | Path | Purpose |
|-------|------|---------|
| domain | `domain/` | entities, value objects, repository protocols, pure domain services |
| application | `application/` | use cases |
| infrastructure | `infrastructure/` | repository implementations |
| interface | `interface/` | {% if cookiecutter.use_web_api == "yes" %}FastAPI endpoints, {% endif %}CLI |
| bootstrap | `bootstrap/` | settings (pydantic-settings), DI container |

**Dependency rule**: `domain` depends on nothing. `application` depends only on `domain`. `infrastructure` implements domain protocols. `interface` calls application use cases. `bootstrap` wires everything. See `docs/DEVELOPMENT_GUIDELINES.md` for full details.

Settings use env prefix `{{ cookiecutter.project_slug | upper }}_` with `__` as the nested delimiter. Loaded from `.env` automatically via Makefile (`uv run --env-file .env`).
{%- if cookiecutter.use_frontend == "yes" %}

Frontend is built to `{{ cookiecutter.project_slug }}/interface/web/static/` and served by FastAPI in production (`make frontend`).
{%- endif %}

## Stack

**Python ({{ cookiecutter.python_version }}+)**
- pydantic / pydantic-settings for models and config
{%- if cookiecutter.use_web_api == "yes" %}
- FastAPI + uvicorn
{%- endif %}
- ruff: 120 char line-length
- pyright: strict type checking
- pytest-asyncio: `asyncio_mode = "auto"` (no manual `@pytest.mark.asyncio` needed)
{%- if cookiecutter.use_frontend == "yes" %}

**TypeScript (web/)**
- React, Vite, Bun
- Feature-Sliced Design: `app/` → `pages/` → `widgets/` → `features/` → `entities/` → `shared/`
- Biome: tabs, double quotes
- Path alias: `@/` → `web/src/`
{%- endif %}

## Gotchas

- Python `PYTHONPATH` is set to project root in Makefile; tests use `pythonpath = ["."]` in pytest config
- No CI workflows — always run `make all` locally before committing
- Test directory structure mirrors source: `tests/unit/domain/entities/test_foo.py` → `{{ cookiecutter.project_slug }}/domain/entities/foo.py`
- All code, comments, docstrings, and docs must be in English
{%- if cookiecutter.use_frontend == "yes" %}
- `web/src/shared/api/generated/` is codegen output — never edit manually; run `make generate-api`
- Frontend build output goes to `{{ cookiecutter.project_slug }}/interface/web/static/` — not committed, rebuilt via `make frontend`
- After adding/changing FastAPI routes, always regenerate the API client (`make generate-api`)
{%- endif %}
