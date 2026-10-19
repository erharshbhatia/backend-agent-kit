# Repository pattern

The data-access standard. A project may also keep a longer binding spec (`implementation/repository-pattern.md`, with a catalog of its repositories); when it exists, it wins over this file. The schema itself is specified in `implementation/database-schema.md`.

## 1. Why

- One place for SQL, so the rest of the code is testable with in-memory twins.
- Transaction boundaries owned by the caller, so one use case writes several entities atomically.
- Concurrency and idempotency guarantees stated in method names and proven by contract tests.

## 2. Structure

```text
<package>/persistence/
  ports/          Protocols only: UnitOfWork + one repository per entity; errors.py; results.py — imports domain types only
  postgres/       the only package allowed to import sqlalchemy / psycopg
    tables.py     SQLAlchemy Core tables: the single source of the schema
    uow.py        PostgresUnitOfWork (one connection + transaction)
    mappers/      row ↔ domain model, one module per entity
    repositories/ one module per repository, implementing its port
    notifier.py   LISTEN/NOTIFY wake-ups, if used
  memory/         in-memory twins for unit tests (store, uow, repositories)
  migrations/     Alembic, checked against tables.py
tests/persistence/contracts/   one suite per repository, parameterized over {postgres, memory}
```

## 3. Interfaces

```python
class UnitOfWork(Protocol):
    @property
    def orders(self) -> OrderRepository: ...          # one read-only property per repository
    async def __aenter__(self) -> Self: ...
    async def __aexit__(self, exc_type, exc, tb) -> None: ...   # rolls back if not committed
    async def commit(self) -> None: ...
    async def rollback(self) -> None: ...

type UnitOfWorkFactory = Callable[[], UnitOfWork]    # injected by bootstrap
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

## 4. Rules

| # | Rule | Enforced by |
| --- | --- | --- |
| R1 | Only `persistence/postgres` imports `sqlalchemy` or `psycopg`. No SQL strings anywhere else. | import-linter |
| R2 | Code outside `persistence` depends only on `persistence.ports`. Only `bootstrap.py` picks an implementation. | import-linter |
| R3 | One repository per entity (or per aggregate when rows are always written together). No generic `query(**filters)`. | Review |
| R4 | Domain models in and out. Rows and ORM objects never leave `postgres/`; mappers translate. | mypy + review |
| R5 | Repositories never commit. The caller owns the transaction. | `commit` exists only on `UnitOfWork` |
| R6 | No business logic in repositories (no retries, no decisions). Data invariants (uniqueness, version checks) are fine. | Review |
| R7 | Repositories never call each other. Cross-entity work belongs to the caller inside one unit of work. | Review |
| R8 | Concurrency is explicit: version checks raise `ConcurrencyConflict` / `LeaseLost`; claims are `claim_*` methods using `FOR UPDATE SKIP LOCKED`. | Contract tests |
| R9 | Idempotent inserts return `Created(x)` / `Existing(x)` instead of raising. | Contract tests |
| R10 | Every list method takes a required `limit`; long lists use keyset pagination (`Page[T]` with a cursor). | Signatures |
| R11 | Every port has a Postgres and a memory implementation and one shared contract suite both pass. | The repository guard in `make check` |
| R12 | `now` is a parameter; never `NOW()` evaluated silently in SQL. | Frozen-clock contract tests |
| R13 | PII fields are mapped in one place (the mapper), so encryption or tokenization later touches only mappers. | Review |
| R14 | Schema change = `tables.py` + Alembic migration + mapper + memory twin + contract suite + `database-schema.md`. | `alembic check` |
| R15 | Core tables are generic: no tenant, customer, or business-flow words in table, column, or repository names (`tenant_id` is the allowed exception). | Domain-word guard |

## 5. Memory twins

- Snapshot isolation: a row changed by two concurrent units of work fails the second commit with `ConcurrencyConflict`.
- Where Postgres resolves a race per statement (`SKIP LOCKED` claims, `ON CONFLICT` inserts), the twin emulates the Postgres outcome so the shared contract suite passes: a row locked by another live transaction is skipped by claims, counts as held for leases, and makes a racing idempotent insert raise `ConcurrencyConflict`.
- Twins need not enforce foreign keys; say so in the twin's docstring.

## 6. Testing

- **Contract suites** (`tests/persistence/contracts/test_<module>.py`): one per port; a `backend` fixture runs each test against Postgres (testcontainer, migrated to head, truncated after each test) and memory. Cover the normal path, duplicates (`Existing`), version conflicts, lease expiry, `claim_*` exclusivity under concurrency, pagination, frozen time.
- **Unit tests** of use cases use memory implementations.
- **Integration and end-to-end tests** use Postgres.
- **Completeness:** a test fails when a `*Repository` Protocol lacks `Postgres<Name>` / `Memory<Name>`, a contract suite, or a `UnitOfWork` property.
- **Migrations:** a test runs `alembic upgrade head` on an empty testcontainer database, then `alembic check`.

## 7. Adding or changing an entity

1. Update `implementation/database-schema.md` (DDL, access pattern → index, migration number) and the repository catalog if the project keeps one.
2. Port method(s) named by intent, with concurrency/idempotency guarantees in the docstring.
3. `tables.py` + migration (forward-only; expand then contract for existing tables).
4. Mapper, Postgres repository, memory twin.
5. Contract tests for the cases in §6.
6. Change record listing the migration and the repository methods added.
