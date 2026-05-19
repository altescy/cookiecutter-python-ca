PWD     := $(shell pwd)
UV_RUN  := $(if $(wildcard .env),uv run --env-file .env,uv run)
PYTHON  := $(UV_RUN) python
PYTEST  := $(UV_RUN) pytest
RUFF    := $(UV_RUN) ruff
PYRIGHT := $(UV_RUN) pyright
{%- if cookiecutter.use_web_api == "yes" %}
UVICORN := $(UV_RUN) uvicorn
{%- endif %}
{%- if cookiecutter.use_frontend == "yes" %}
BUN     := bun
{%- endif %}

PROJECT_SLUG := {{ cookiecutter.project_slug }}
{%- if cookiecutter.use_web_api == "yes" %}
PROJECT_PORT := 8000
{%- endif %}

.PHONY: help
help:
	@echo "Usage:"
	@echo "  make <target>"
	@echo ""
	@echo "Targets:"
	@echo "  help              Show this help message"
	@echo ""
	@echo "  Development:"
	@echo "  all               Run format, lint, and test"
	@echo "  format            Format code"
	@echo "  lint              Lint and type-check"
	@echo "  test              Run tests"
	@echo "  clean             Remove generated files"
{%- if cookiecutter.use_web_api == "yes" %}
	@echo "  serve             Start development server"
{%- endif %}
{%- if cookiecutter.use_frontend == "yes" %}
	@echo "  frontend          Build frontend assets"
	@echo "  generate-api      Regenerate API client from OpenAPI schema"
{%- endif %}

.PHONY: setup
setup:
	uv sync --dev --all-extras
	cd web && bun install

.PHONY: all
all: format lint test

## Development

.PHONY: format
format: format-python{% if cookiecutter.use_frontend == "yes" %} format-typescript{% endif %}

.PHONY: format-python
format-python:
	PYTHONPATH=$(PWD) $(RUFF) check --select I --fix
	PYTHONPATH=$(PWD) $(RUFF) format

{%- if cookiecutter.use_frontend == "yes" %}

.PHONY: format-typescript
format-typescript:
	cd web && $(BUN) run format
{%- endif %}

.PHONY: lint
lint: lint-python{% if cookiecutter.use_frontend == "yes" %} lint-typescript{% endif %}

.PHONY: lint-python
lint-python:
	PYTHONPATH=$(PWD) $(RUFF) check
	PYTHONPATH=$(PWD) $(PYRIGHT)

{%- if cookiecutter.use_frontend == "yes" %}

.PHONY: lint-typescript
lint-typescript:
	cd web && $(BUN) run lint
{%- endif %}

.PHONY: test
test: test-python{% if cookiecutter.use_frontend == "yes" %} test-typescript{% endif %}

.PHONY: test-python
test-python:
	PYTHONPATH=$(PWD) $(PYTEST) $(PWD)/tests

{%- if cookiecutter.use_frontend == "yes" %}

.PHONY: test-typescript
test-typescript:
	cd web && $(BUN) run test
{%- endif %}

.PHONY: clean
clean:
	rm -rf .pytest_cache .ruff_cache
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

{%- if cookiecutter.use_web_api == "yes" %}

.PHONY: serve
serve:
	PYTHONPATH=$(PWD) $(UVICORN) $(PROJECT_SLUG).interface.web.app:create_app --factory --reload --host 127.0.0.1 --port $(PROJECT_PORT)
{%- endif %}

{%- if cookiecutter.use_frontend == "yes" %}

.PHONY: frontend
frontend:
	rm -rf $(PROJECT_SLUG)/interface/web/static
	cd web && $(BUN) run build

.PHONY: generate-api
generate-api:
	$(eval OPENAPI_SCHEMA := $(shell mktemp))
	$(PYTHON) -c "import json; from $(PROJECT_SLUG).interface.web.app import create_app; json.dump(create_app().openapi(), open('$(OPENAPI_SCHEMA)', 'w'), indent=2, ensure_ascii=False)"
	cd web && $(BUN) run generate-api -- --input $(OPENAPI_SCHEMA)
	rm -f $(OPENAPI_SCHEMA)
{%- endif %}
