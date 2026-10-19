# Stack

Profile `python-postgres` (`engineering-standards/references/stacks/python-postgres.md`), as shipped by `scaffolds/python-service/`. Bootstrap copies this file into the project and replaces `app` / `APP_` with the project's names.

| | |
| --- | --- |
| Profile | python-postgres |
| Stack ADR | ADR-0002 |
| Package root | `app/src/app/` |
| Env prefix | `APP_` |

## Commands

| Abstract name | Concrete command | Needs |
| --- | --- | --- |
| `check` | `make check` (ruff lint + format check, mypy --strict, import-linter, three guards, pytest excluding `db`/`external`) | nothing |
| `check-all` | `make check-all` (check + `make test-db` + `make migrations-check`) | Docker |
| `test` | `make test` (`pytest -m "not db and not external"`) | nothing |
| `test-db` | `make test-db` (`pytest -m db`, testcontainers Postgres) | Docker |
| `test-external` | `make test-external` (`pytest -m external`; exit 0 while none exist) | keys, owner's go-ahead |
| `e2e` | `make e2e` (`pytest tests/scenarios`) | Docker if a scenario is marked `db` |
| `migrations-check` | `make migrations-check` (`alembic check`, after `make up && make migrate`) | Docker |
| `deps-sync` | `make sync` (`uv sync`) | network |
| `deps-lock` | `make lock` (`uv lock`) | network |
| `up` / `migrate` / `stack` / `down` | `make up` / `make migrate` / `make stack` / `make down` | Docker |

## Tools

| Role | Tool | Config |
| --- | --- | --- |
| Linter and formatter | ruff | `pyproject.toml` `[tool.ruff]` |
| Type checker (strictest mode) | mypy `--strict` with the pydantic plugin | `pyproject.toml` `[tool.mypy]` |
| Layer-contract tool | import-linter | `.importlinter`, custom contracts in `scripts/importlinter_contracts.py` |
| Banned-API tool | ruff `flake8-tidy-imports` banned-api (`datetime.now`, `uuid4`, `os.environ`, …) | `pyproject.toml` |
| Domain-word, SQL-location, repository guards | `scripts/check_domain_words.py`, `check_sql_location.py`, `check_repositories.py` | `scripts/guards.toml` |
| Test runner, property testing, test containers | pytest + pytest-asyncio, Hypothesis, testcontainers | `pyproject.toml` `[tool.pytest.ini_options]`, markers `db` and `external` with `--strict-markers` |
| Migration tool | Alembic | `alembic.ini`, `app/src/app/persistence/migrations/` |

## Files behind the abstract names

| Abstract name | File |
| --- | --- |
| Composition root | `app/src/app/bootstrap.py` |
| Settings module | `app/src/app/settings.py` (pydantic-settings, nested with `__`) |
| Dependency manifest | `pyproject.toml` (workspace root) and `app/pyproject.toml` |
| Lock file | `uv.lock` |
| Schema source of truth | `app/src/app/persistence/postgres/tables.py` |
| Persistence adapter package (the only SQL) | `app/src/app/persistence/postgres/` |
| Memory twins package | `app/src/app/persistence/memory/` |
| Contract-suite directory | `tests/persistence/contracts/` |
| Env example file | `.env.example` |
| Entrypoints | `app/src/app/entrypoints/{api,worker,cli}.py`; API served by uvicorn `app.bootstrap:create_app --factory` |

## Store primitives

| Need | This stack |
| --- | --- |
| Atomic claim of queued work | `SELECT … FOR UPDATE SKIP LOCKED` |
| Idempotent insert | `INSERT … ON CONFLICT DO NOTHING RETURNING` |
| Wake-up for workers | LISTEN/NOTIFY on a session-mode connection, polling as fallback |
| Time-ordered unique ids | UUIDv7 (`app.domain.ids.UuidV7Generator`) |
