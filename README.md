# cookiecutter-python-ca

A [Cookiecutter](https://cookiecutter.readthedocs.io) template for Python applications following **Clean Architecture**.

## Features

- Clean Architecture layers: `domain` / `application` / `infrastructure` / `interface` / `bootstrap`
- [uv](https://docs.astral.sh/uv/) for dependency management
- [ruff](https://docs.astral.sh/ruff/) for formatting and linting
- [pyright](https://github.com/microsoft/pyright) in strict mode for type checking
- [pytest](https://docs.pytest.org) with `asyncio_mode = "auto"`
- [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) for configuration
- Optional **FastAPI + uvicorn** web API interface
- Optional **React + Vite + Biome** frontend (requires web API)
- Minimal **Feature-Sliced Design** frontend with **Steiger** architecture checks
- `AGENTS.md` and `docs/DEVELOPMENT_GUIDELINES.md` included in every generated project

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- [cookiecutter](https://cookiecutter.readthedocs.io) (`uv tool install cookiecutter`)
- [bun](https://bun.sh) — only if `use_frontend = yes`

## Usage

```bash
cookiecutter gh:altescy/cookiecutter-python-ca
```

Or from a local clone:

```bash
cookiecutter path/to/cookiecutter-python-ca
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `project_name` | `My Python App` | Human-readable project name |
| `project_slug` | _(derived)_ | Python package name (auto-derived from `project_name`) |
| `project_description` | `A Python application` | Short description |
| `author_name` | `Your Name` | Author name |
| `author_email` | `you@example.com` | Author email |
| `python_version` | `3.12` | Minimum Python version (`3.12` or `3.13`) |
| `use_web_api` | `yes` | Include FastAPI web interface (`yes` / `no`) |
| `use_frontend` | `yes` | Include React/Vite frontend (`yes` / `no`, requires `use_web_api = yes`) |

## Generated Structure

```
<project_slug>/
├── AGENTS.md                        # Quick reference for developers and AI agents
├── docs/
│   └── DEVELOPMENT_GUIDELINES.md    # Architecture rules and coding conventions
├── Makefile                         # Development workflow
├── pyproject.toml
├── <project_slug>/
│   ├── domain/
│   │   ├── entities/
│   │   ├── repositories/            # typing.Protocol interfaces
│   │   ├── services/                # Pure domain services
│   │   ├── value_objects/
│   │   └── errors.py
│   ├── application/
│   │   └── usecases/
│   ├── infrastructure/
│   │   └── repositories/
│   ├── interface/
│   │   ├── cli/
│   │   └── web/                     # FastAPI (if use_web_api = yes)
│   └── bootstrap/
│       ├── settings.py              # pydantic-settings
│       └── container.py             # DI container
├── tests/
│   ├── unit/
│   │   ├── domain/
│   │   ├── application/
│   │   └── infrastructure/
│   └── integration/
│       └── web/                     # FastAPI TestClient tests (if use_web_api = yes)
└── web/                             # React + Vite frontend (if use_frontend = yes)
    └── src/
        ├── main.tsx
        ├── app/                     # Composition and global styles
        ├── pages/home/              # Page slice with an index.ts public API
        └── shared/api/              # HTTP client factories and generated SDK
```

## Getting Started (generated project)

```bash
cd <project_slug>
uv sync --group dev
cp .env.example .env

make all        # format + lint + test
make serve      # start dev server (if use_web_api = yes)
```

## Architecture

The generated project enforces a strict dependency rule:

```
interface ──→ application ──→ domain ←── infrastructure
```

- **`domain/`** — pure Python, no third-party dependencies. Entities, repository protocols (`typing.Protocol`), and domain services (no IO, no async).
- **`application/`** — use cases that orchestrate domain objects. Depends on `domain` only.
- **`infrastructure/`** — implements the repository protocols defined in `domain`. Contains all external-facing code (databases, APIs, etc.).
- **`interface/`** — delivery mechanisms (CLI, HTTP). Thin handlers that call use cases and serialize results.
- **`bootstrap/`** — wires all layers together. Contains `AppSettings` and the DI `Container`.

The frontend follows Feature-Sliced Design: `app → pages → widgets → features → entities → shared`.
Only `app`, `pages/home`, and `shared/api` are included initially; add other layers when needed.
Steiger checks layer dependencies and public API boundaries as part of `make lint` and `make all`.
FSD does not require a particular state management or CSS library.

## Template Tests

```bash
uv sync --group dev
uv run pytest tests/ -v
```

Tests generate projects for all option combinations and verify:

- Correct file structure (files present / absent based on options)
- `make all` completes successfully in each generated project
