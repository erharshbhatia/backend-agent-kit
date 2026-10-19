# python-service scaffold

A small, working starting point for a Python backend that follows `engineering-standards`: layers pointing inward, ports and adapters, repository pattern with a unit of work, injected time and ids, structured logs, and every rule enforced by `make check`.

It runs as-is. The package is literally named `app`; rename it when you start a project (see the `project-bootstrap` skill).

## What's inside

| Path | What it is |
| --- | --- |
| `app/src/app/settings.py` | All settings (pydantic-settings, `APP_` prefix). The only environment reader |
| `app/src/app/bootstrap.py` | Composition root: builds the `Container`, the API app, the worker, the CLI |
| `app/src/app/domain/` | Pure code. Ships `Clock` and `IdGenerator` (UUIDv7) |
| `app/src/app/application/` | Use cases. Ships `check_readiness` |
| `app/src/app/entrypoints/` | `api.py` (`/livez`, `/readyz`), `worker.py` (tick loop), `cli.py` (`appctl`) |
| `app/src/app/persistence/` | `ports/` (Protocols, plus `errors.py` and `results.py`: `ConcurrencyConflict`, `LeaseLost`, `Created | Existing`, `Page`), `postgres/` (the only SQL), `memory/` (test twins), `migrations/` (Alembic) |
| `app/src/app/observability/logging.py` | structlog: console locally, JSON in containers |
| `.importlinter` + `scripts/importlinter_contracts.py` | Layer and vendor contracts |
| `scripts/guards.toml` | Config for the domain-word, SQL-location, and repository guards |
| `scripts/check_*.py` | The three guards |
| `tests/` | Unit tests; `scenarios/` holds end-to-end scenarios (S0: the service boots); `persistence/contracts/` explains the contract-suite pattern |
| `docker-compose.yml`, `Dockerfile` | Postgres → migrate → api + worker, ports on 127.0.0.1 |

## Commands

```bash
uv sync                 # install (creates uv.lock; commit it)
make check              # lint, format check, mypy --strict, import contracts, guards, unit tests
make up && make migrate # Postgres 16 on 127.0.0.1:55432 and the baseline migration
make test-db            # Postgres tests (testcontainers; needs Docker)
make e2e                # end-to-end scenarios in tests/scenarios (S0 ships with the scaffold)
make test-external      # tests marked external (needs keys; passes while none exist)
make check-all          # check + test-db + alembic check
make stack              # the whole system in containers (API on 127.0.0.1:8080)
uv run appctl --help    # operator CLI
```

`make check` needs no Docker and no external keys, so every agent can run it in its own worktree or copy.

Several projects on one machine: give each its own host ports with `APP_PG_HOST_PORT` and `APP_API_HOST_PORT` (defaults 55432 and 8080) before `make up` or `make stack`, or the second project's Postgres fails to bind.
