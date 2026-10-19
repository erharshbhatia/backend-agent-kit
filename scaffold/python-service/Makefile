# Local developer commands. `make check` = every gate that needs no Docker and no external keys.

UV ?= uv
RUN := $(UV) run

.DEFAULT_GOAL := help
.PHONY: help sync up down stack stack-logs migrate test test-db lint fmt typecheck imports guards migrations-check check check-all

help: ## List targets
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-18s %s\n", $$1, $$2}'

sync: ## Install the workspace and dev tools (uv.lock)
	$(UV) sync

up: ## Start Postgres only and wait until it is healthy (processes run from source)
	docker compose up -d --wait postgres

stack: ## Build and start the whole system and wait until healthy
	docker compose up -d --build --wait

stack-logs: ## Follow the logs of the whole system
	docker compose logs -f

down: ## Stop the compose services (data volume kept)
	docker compose down

migrate: ## Apply Alembic migrations to the dev database
	$(RUN) alembic upgrade head

test: ## Unit and application tests (no Docker)
	$(RUN) pytest -m "not db and not external"

test-db: ## Repository contract and other Postgres tests (testcontainers; needs Docker)
	$(RUN) pytest -m db

lint: ## Ruff lint + format check
	$(RUN) ruff check .
	$(RUN) ruff format --check .

fmt: ## Format and auto-fix
	$(RUN) ruff format .
	$(RUN) ruff check --fix .

typecheck: ## mypy --strict
	$(RUN) mypy

imports: ## import-linter layer and vendor contracts
	$(RUN) lint-imports

guards: ## Domain-word, SQL-location, and repository-completeness guards
	$(RUN) python scripts/check_domain_words.py
	$(RUN) python scripts/check_sql_location.py
	$(RUN) python scripts/check_repositories.py

migrations-check: ## tables.py and migrations agree (needs `make up && make migrate`)
	$(RUN) alembic check

check: lint typecheck imports guards test ## All gates that need no Docker

check-all: check test-db migrations-check ## Everything, including Postgres
