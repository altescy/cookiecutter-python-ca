# Development Guidelines

This document defines the rules and conventions that **must** be followed when working on this codebase.
Every contributor (human or AI agent) should read this before making changes.

## Language

- All code, comments, docstrings, commit messages, and documentation are in **English**.

---

## Backend (Python)

### Clean Architecture — Dependency Rule

```
interface ──→ application ──→ domain ←── infrastructure
                                  ↑
                               bootstrap
```

| Layer | May depend on | Must NOT depend on |
|-------|---------------|--------------------|
| `domain/` | stdlib, typing only | application, infrastructure, interface, third-party libs |
| `application/` | domain | infrastructure, interface |
| `infrastructure/` | domain (protocols) | interface |
| `interface/` | application (use cases) | infrastructure directly |
| `bootstrap/` | all layers (wiring only) | — |

**Violations of this rule are the highest-priority issue to fix.**

### Domain Layer Rules

- Entities use `@dataclass(frozen=True, slots=True)`.
- Value objects are immutable and self-validating (`__post_init__`).
- Repository interfaces are `typing.Protocol` classes — never ABCs.
- Domain services are **pure**: no IO, no repository access, no async. They receive data and return results.
- Domain errors inherit from `DomainError` and carry structured context (not just message strings).
- Use `NewType` for domain IDs (e.g., `ItemId = NewType("ItemId", str)`) — never bare `str`.

### Application Layer Rules

- Use cases are the sole entry point for business operations.
- Each use case is a single class with an `async def execute(...)` method.
- Use cases orchestrate: they call repositories, invoke domain services, and compose results.
- Never import from `infrastructure` or `interface`.

### Infrastructure Layer Rules

- Implements repository protocols defined in `domain/repositories/`.
- Repositories receive a DB connection factory (`Callable[[], Awaitable[Connection]]`), not a raw connection — this enables lazy initialization and testing.
- Never put business logic in repository implementations.

### Interface Layer Rules

- Route handlers are thin: validate input → call use case → serialize output.
- Domain errors propagate to `handlers.py` which maps them to HTTP status codes.
- Never put business logic in route handlers or CLI commands.
{%- if cookiecutter.use_web_api == "yes" %}
- List endpoints must support pagination (`offset`, `limit` query params).
- All error responses use a consistent schema: `{ "detail": string, "error_type": string }`.
{%- endif %}

### Type Safety

- `pyright` in strict mode — all code must pass without errors.
- Use `NewType` for domain IDs.
- Prefer `Protocol` over `ABC` for interfaces.
- All function signatures must have explicit return type annotations.
- Avoid `Any` — use generics or `object` when the type is truly unknown.

### Style

- Line length: 120 characters (ruff).
- No comments in code unless explaining a non-obvious "why" (never explain "what").
- Imports sorted by ruff (`isort` compatible).

---
{%- if cookiecutter.use_frontend == "yes" %}

## Frontend (TypeScript / React)

### Feature-Sliced Design — Import Rule

```
app → pages → widgets → features → entities → shared
```

- Higher layers may only import from **lower** layers.
- Cross-slice imports within the same layer are **forbidden**.
- All imports from a slice must go through its `index.ts` (public API).

### Segment Conventions

| Segment | Purpose |
|---------|---------|
| `ui/` | React components (presentational) |
| `model/` | State (Jotai atoms), types, hooks |
| `api/` | Data fetching, API call wrappers |

### Type Safety

- `strict: true` in tsconfig — no implicit any.
- Never manually edit `shared/api/generated/` — run `make generate-api`.
- Prefer type inference; add explicit annotations only when inference fails or for public APIs.

### Style

- Formatter: Biome (tabs, double quotes).
- No inline styles — use Tailwind CSS classes.
- State: Jotai atoms for shared state; `useState` only for component-local ephemeral state.

---
{%- endif %}

## Testing

### Python Test Structure

Test directory structure **mirrors** the source module structure:

```
tests/unit/domain/entities/test_item.py       →  {{ cookiecutter.project_slug }}/domain/entities/item.py
tests/unit/application/usecases/test_items.py →  {{ cookiecutter.project_slug }}/application/usecases/items.py
tests/unit/infrastructure/repositories/...   →  {{ cookiecutter.project_slug }}/infrastructure/repositories/...
```

### Test Principles

- Domain layer tests: pure unit tests, no mocks, no IO.
- Application layer tests: use in-memory fakes or `unittest.mock` for repositories.
- Infrastructure layer tests: integration tests with real in-memory storage (e.g., `:memory:` for SQLite).
{%- if cookiecutter.use_web_api == "yes" %}
- Integration (API) tests: use FastAPI `TestClient` with dependency overrides.
{%- endif %}
- `asyncio_mode = "auto"` — do NOT add `@pytest.mark.asyncio` manually.
- Shared fixtures go in `tests/conftest.py` or `tests/{unit,integration}/conftest.py`.
{%- if cookiecutter.use_frontend == "yes" %}

### Frontend Tests

- Place tests in `__tests__/` within the relevant segment.
- Test atoms and logic — not component rendering (unless behavior is complex).
- Use vitest.
{%- endif %}

---
{%- if cookiecutter.use_web_api == "yes" %}

## API Contract

- After adding or changing any FastAPI route, **always** run `make generate-api` to regenerate the frontend client.
- List endpoints must support pagination (`offset`, `limit` query params).
- All error responses use: `{ "detail": string, "error_type": string }`.

---
{%- endif %}

## Git & Workflow

- Run `make all` (format + lint + test) before every commit.
- Commit messages: imperative mood, English, concise (e.g., `add item CRUD endpoints`).
- Do not commit: `.env`{% if cookiecutter.use_frontend == "yes" %}, `web/src/shared/api/generated/`, `{{ cookiecutter.project_slug }}/interface/web/static/`{% endif %}.
- One logical change per commit.

---

## Adding Dependencies

- Add Python packages via `uv add <pkg>` and verify they install on Python {{ cookiecutter.python_version }}.
- Prefer slim/minimal package variants when available.
{%- if cookiecutter.use_frontend == "yes" %}
- Frontend: use `bun add` — verify no peer dependency conflicts.
{%- endif %}
- Document the rationale in a commit message or PR description.
