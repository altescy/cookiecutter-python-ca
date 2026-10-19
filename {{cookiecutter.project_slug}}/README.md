# {{ cookiecutter.project_name }}

{{ cookiecutter.project_description }}

## Setup

```bash
uv sync --group dev
cp .env.example .env
{%- if cookiecutter.use_frontend == "yes" %}
cd web && bun install && cd ..
{%- endif %}
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
{%- if cookiecutter.use_frontend == "yes" %}

### Frontend — Feature-Sliced Design

```text
web/src/
├── main.tsx              # Mount the application
├── app/                  # Composition and global styles
├── pages/home/           # Home page slice; index.ts is its public API
│   └── ui/
└── shared/api/           # Public API boundary and generated API client
```

Add `widgets/`, `features/`, and `entities/` only when needed. Dependencies point downward:
`app → pages → widgets → features → entities → shared`.
Import slices through their public APIs, for example `@/pages/home`.

`make lint-typescript` runs Biome, TypeScript, and Steiger architecture checks.
To run only architecture checks: `cd web && bun run lint:architecture`.
Run `make generate-api` after changing FastAPI routes; do not edit `shared/api/generated/` manually.
See `docs/DEVELOPMENT_GUIDELINES.md` for layer responsibilities and extension examples.

### Frontend Serving

Run `make frontend` to build static files into `{{ cookiecutter.project_slug }}/interface/web/static/`,
then start FastAPI with `make serve`. FastAPI's `app.frontend()` serves the build at `/` and handles
SPA navigation with an `index.html` fallback. API routes and `/docs` take precedence.
The fallback requires a `GET` or `HEAD` request explicitly accepting HTML. Normal asset requests
and JSON requests for missing paths return `404` rather than the SPA HTML.

During development, run Vite separately (`cd web && bun run dev`); `/api` is proxied to FastAPI.
When the build directory is absent, FastAPI still starts and serves the API without registering a frontend.
{%- endif %}
