# Profile: python-postgres

Python 3.12 with PostgreSQL 16. Scaffold: `scaffolds/python-service/`. Sections follow the contract in `README.md`.

## 1. Stack table

The rows `project-bootstrap` copies into `project-guide/knowledge/STACK.md`.

| Abstract name | Concrete |
| --- | --- |
| Language, packaging | Python 3.12, uv workspace (`pyproject.toml` at the root and in the package) |
| Web framework | FastAPI, served by uvicorn (`--factory` on the composition root) |
| Database, driver | PostgreSQL 16; SQLAlchemy 2 async Core + psycopg 3 |
| Migration tool | Alembic |
| Typed boundary models | Pydantic v2; settings via pydantic-settings |
| Logging module | structlog, `observability/logging.py` |
| Test runner | pytest with pytest-asyncio (`asyncio_mode = "auto"`), Hypothesis for properties, testcontainers for Postgres, respx for HTTP mocking |
| Linter/formatter | ruff (lint + format) |
| Type checker | mypy `--strict` with the pydantic plugin |
| Layer-contract tool | import-linter (`.importlinter`, custom contract types in `scripts/importlinter_contracts.py`) |
| Banned-API tool | ruff `flake8-tidy-imports.banned-api` (wall clock, random ids, environment reads) |
| Domain-word guard | `scripts/check_domain_words.py`, config `scripts/guards.toml` |
| SQL-location guard | `scripts/check_sql_location.py` |
| Repository guard | `scripts/check_repositories.py` |
| Package root | `<package>/src/<package>/` (the scaffold uses `app`) |
| Composition root | `bootstrap.py` |
| Settings module | `settings.py` (env prefix `APP_` in the scaffold, nested with `__`) |
| Dependency manifest, lock file | `pyproject.toml`, `uv.lock` |
| Schema source of truth | `persistence/postgres/tables.py` (SQLAlchemy Core tables) |
| Persistence adapter package | `persistence/postgres/` |
| Memory twins package | `persistence/memory/` |
| Contract-suite directory | `tests/persistence/contracts/` |
| `check` | `make check` = ruff check, ruff format --check, mypy, lint-imports, the three guards, `pytest -m "not db and not external"` |
| `check-all` | `make check-all` = `make check` + `make test-db` + `make migrations-check` |
| `test` | `make test` = `pytest -m "not db and not external"` |
| `test-db` | `make test-db` = `pytest -m db` (testcontainers; needs Docker) |
| `test-external` | `make test-external` = `pytest -m external` (passes with exit 5 when none exist) |
| `e2e` | `make e2e` = `pytest tests/scenarios -m "not external"` |
| `migrations-check` | `make migrations-check` = `alembic check` (after `make up && make migrate`) |
| `deps-sync` | `uv sync` |
| `deps-lock` | `uv lock` |
| Local database | `make up` (compose, Postgres on `127.0.0.1:${APP_PG_HOST_PORT:-55432}`), `make migrate`; `make stack` for the whole system |

## 2. Layout

```text
<package>/src/<package>/
  entrypoints/      api.py (FastAPI routers: /livez, /readyz), worker.py (tick loop), cli.py (typer) — thin
  application/      use cases (ships check_readiness)
  domain/           pure: clock.py (Clock, SystemClock, FrozenClock), ids.py (IdGenerator, UuidV7Generator, SeededIdGenerator)
  persistence/
    ports/          database.py, uow.py, errors.py (ConcurrencyConflict, LeaseLost), results.py (Created, Existing, InsertResult, Page)
    postgres/       db.py (engine, PostgresDatabase), tables.py, uow.py (PostgresUnitOfWork), repositories/, mappers/ (with the first entity)
    memory/         uow.py (MemoryDatabase, MemoryUnitOfWork), repositories/
    migrations/     Alembic env.py, versions/0001_baseline.py
  observability/    logging.py (structlog configuration, get_logger, reset_logging)
  bootstrap.py      Container (frozen dataclass), build_container, create_app, run_cli
  settings.py       pydantic-settings
tests/
  conftest.py       frozen_clock, seeded_ids, isolated logging
  unit/             domain and application tests
  scenarios/        end-to-end, one module per scenario id (ships S0)
  persistence/contracts/   one suite per repository port
scripts/            the three guards, guards.toml, importlinter_contracts.py
```

## 3. Idioms

Numbered as in `clean-code.md`.

1. **Naming.** snake_case functions and modules, PascalCase classes, UPPER_CASE constants. Typer command names in kebab-case (`db-ping`).
2. **Functions and modules.** Keyword-only parameters after `*` for anything beyond two parameters or any boolean. ruff `B`, `SIM`, `RET`, `PIE`, `C4` rules keep functions small and direct.
3. **Types and data.** `mypy --strict` with `warn_unreachable`; Pydantic v2 models at boundaries with `init_forbid_extra`; frozen dataclasses (`slots=True`) or Pydantic for domain values; discriminated unions `Annotated[A | B, Field(discriminator="type")]`; exhaustive `match` with `assert_never`; `Decimal` for money, tz-aware UTC `datetime`, `timedelta` for durations; ids as `NewType("OrderId", UUID)` generated as UUIDv7 by `IdGenerator`. PEP 695 generics (`class Created[T]`, `type InsertResult[T] = ...`).
4. **Errors.** Project hierarchy under `domain/errors.py`; persistence failures in `persistence/ports/errors.py` (`PersistenceError` base). Never `except Exception: pass`; ruff `BLE`/`B` flag bare excepts. ruff `N818` is ignored so failure names need no `Error` suffix.
5. **Async and I/O.** Async end to end: FastAPI, httpx, psycopg async. `asyncio.TaskGroup` or a bounded semaphore; no bare `create_task` without a holder. Timeouts from settings per operation.
6. **Comments.** `# OR-12: …` and `# TODO(P04-F2): …`.
7. **Logging.** `log = get_logger(__name__)` at module level; `log.info("order.placed", order_id=..., total=...)`; console renderer when `LOGGING__FORMAT=console`, JSON when `json` (set by the container image). `reset_logging()` in test fixtures.
8. **Configuration.** `Settings(BaseSettings)` with `env_prefix`, `env_nested_delimiter="__"`, `.env` loaded automatically; the only module allowed to touch `os.environ` (ruff banned-api `TID251` everywhere else, per-file-ignored in `settings.py`, `domain/clock.py`, `domain/ids.py`, `tests/**`, `scripts/**`).
9. **Dependencies.** `uv add`, lock with `uv lock`, commit `uv.lock`. `uv_build` backend; `requires-python = ">=3.12,<3.13"`.

## 4. Repository implementation

Ports are `typing.Protocol` classes:

```python
class UnitOfWork(Protocol):
    @property
    def orders(self) -> OrderRepository: ...          # one read-only property per repository
    async def __aenter__(self) -> Self: ...
    async def __aexit__(self, exc_type, exc, tb) -> None: ...   # rolls back if not committed
    async def commit(self) -> None: ...
    async def rollback(self) -> None: ...

UnitOfWorkFactory = Callable[[], UnitOfWork]         # injected by bootstrap
```

```python
class OrderRepository(Protocol):                     # example entity
    async def add(self, order: Order) -> InsertResult[Order]:
        """Insert; returns Existing(order) if the same idempotency key was already stored."""
    async def get(self, order_id: OrderId) -> Order | None: ...
    async def save(self, order: Order, *, expected_version: int) -> None:
        """Persist and bump version. Raises ConcurrencyConflict if the version moved."""
    async def claim_due(self, *, now: datetime, limit: int) -> list[Order]:
        """Claim up to `limit` due rows with FOR UPDATE SKIP LOCKED; safe across processes."""
```

Usage:

```python
async with uow_factory() as uow:
    order = await uow.orders.get(order_id)
    ...
    await uow.orders.save(order, expected_version=order.version)
    await uow.outbox.enqueue(message)
    await uow.commit()          # only the unit of work commits
```

- **Schema source of truth:** `persistence/postgres/tables.py`, SQLAlchemy Core `Table` objects in one `MetaData` with the project schema. Alembic `env.py` targets that metadata; `alembic check` fails when tables and migrations disagree. Migrations are forward-only; expand then contract for existing tables.
- **Unit of work:** `PostgresUnitOfWork(engine)` opens one connection and one transaction in `__aenter__`, rolls back in `__aexit__` unless `commit()` was called. Repositories receive the connection; they never commit.
- **Atomic claim:** `SELECT … FOR UPDATE SKIP LOCKED LIMIT :limit` inside the unit of work, then `UPDATE` the claimed rows with the lease owner and expiry in the same transaction.
- **Idempotent insert:** `INSERT … ON CONFLICT (idempotency_key) DO NOTHING RETURNING *`; no row returned means `Existing`, then read the stored row.
- **Version check:** `UPDATE … WHERE id = :id AND version = :expected RETURNING version`; zero rows raises `ConcurrencyConflict`.
- **Wake-ups:** `LISTEN/NOTIFY` through `persistence/postgres/notifier.py` when used. A connection through a transaction-mode pooler (PgBouncer in transaction mode) never receives notifications; `LISTEN` needs a direct or session-mode connection.
- **Connections:** processes × (pool + overflow + dedicated LISTEN connection) must stay under `max_connections` (100 default, 3 reserved); the settings `DB__POOL_SIZE` and `DB__MAX_OVERFLOW` size the pool per process.
- **Mappers:** `persistence/postgres/mappers/<entity>.py`, `to_row(model) -> dict` and `from_row(row) -> Model`; PII columns are handled only there (R13).

## 5. Testing

| Pyramid row | Tools |
| --- | --- |
| Domain | pytest, Hypothesis |
| Handlers, Application | pytest with memory repositories and fakes |
| Runtime | Hypothesis `RuleBasedStateMachine` |
| Contracts | pytest parameterized over `{postgres, memory}`; testcontainers `postgres:16-alpine`; respx for httpx |
| End-to-end | pytest in `tests/scenarios/`, httpx `ASGITransport` against the real FastAPI app |
| Model quality | per the test-policy ADR |

- **Tags** are pytest markers registered in `pyproject.toml` with `--strict-markers`: `db` and `external`. `filterwarnings = ["error"]` turns warnings into failures.
- **Determinism:** `FrozenClock(at)` with `advance(timedelta)`, `SeededIdGenerator(seed)`; fixtures `frozen_clock` and `seeded_ids` in `tests/conftest.py`.
- **Contract-suite fixture shape** (`tests/persistence/contracts/README.md`): a session-scoped `postgres_url` fixture starts `PostgresContainer("postgres:16-alpine", driver="psycopg")`, runs `alembic upgrade head` against it, yields the URL; each suite's `backend` fixture is parameterized over the Postgres and memory implementations and truncates tables after each test. Suites are named `test_<port module>.py`; the repository guard fails `make check` when a port has none.
- **Migrations test:** `alembic upgrade head` on the empty container, then `alembic check`.
- **Commands:** the Makefile targets in §1. `make check` runs with no Docker and no keys, so every agent can run it in its own copy or worktree.

## 6. Enforcement map

| Rule | Enforced by | Where |
| --- | --- | --- |
| 1 Layers point inward | import-linter `layers` contract (`bootstrap > entrypoints > application > domain`), `domain-pure` forbidden contract | `.importlinter` |
| 2 Ports not vendors | import-linter `protected_if_present` per vendor package (sqlalchemy/psycopg/alembic only in `persistence.postgres`); add one per SDK | `.importlinter` |
| 3 Repositories in a unit of work | `sql-only-in-postgres` contract; SQL-location guard; `implementations-only-in-bootstrap` contract; repository guard (R11) | `.importlinter`, `scripts/` |
| 4 Registries | Review | `review-checklist.md` |
| 5 Typed contracts | mypy `--strict`, pydantic mypy plugin | `pyproject.toml` |
| 6 Errors as values | Review; ruff bare-except rules | `pyproject.toml` |
| 7 Pure business logic | `domain-pure` contract (no persistence, settings, logging, I/O libraries in `domain`) | `.importlinter` |
| 8 Injected time and ids | ruff banned-api: `datetime.now/utcnow/today`, `date.today`, `time.time/time_ns`, `uuid.uuid1/uuid4`, `os.environ/getenv` | `pyproject.toml` |
| 9 Vocabulary | domain-word guard over `guarded_dirs` with `forbidden_words` and an `allow` list | `scripts/guards.toml` |
| 10 Tests per layer | pytest markers with `--strict-markers`; `make check` vs `make check-all` | `pyproject.toml`, `Makefile` |
| R1, R2 | import-linter contracts above; SQL-location guard | `.importlinter`, `scripts/guards.toml` |
| R4 | mypy + review | |
| R8, R9, R12 | contract suites (frozen clock, concurrency cases) | `tests/persistence/contracts/` |
| R11 | repository guard: every `<Name>Repository` port needs `Postgres<Name>Repository`, `Memory<Name>Repository`, `test_<module>.py` | `scripts/check_repositories.py` |
| R14 | `alembic check` | `Makefile` `migrations-check` |
| R15 | domain-word guard | `scripts/guards.toml` |

## 7. Scaffold

`scaffolds/python-service/`. Runs as-is with the package literally named `app`, env prefix `APP_`, CLI `appctl`, schema `app`, compose project `app`; the renames for a project are in its `BOOTSTRAP.md`, and its `STACK.md` is the filled stack table for this profile. It ships everything in §2, the three guards, the import-linter contracts, the Makefile targets in §1, `docker-compose.yml` (Postgres → migrate → api + worker, ports on `127.0.0.1`) and the `Dockerfile`. Renaming for a project (package, prefix, CLI, schema, compose names) is described in `project-bootstrap` and the scaffold's own README; after renaming, `grep -rn '\bapp\b\|APP_\|appctl'` over the package, scripts, tests and config files should show only intended hits. Several projects on one machine set `APP_PG_HOST_PORT` and `APP_API_HOST_PORT` so compose ports do not collide.
