# Repository pattern

The data-access standard. A project may also keep a longer binding spec (`implementation/repository-pattern.md`, with a catalog of its repositories); when it exists, it wins over this file. The schema itself is specified in `implementation/database-schema.md`. This file holds the rules; the code for the project's language and database is in `stacks/<profile>.md`.

## 1. Why

- One place for SQL, so the rest of the code is testable with in-memory twins.
- Transaction boundaries owned by the caller, so one use case writes several entities atomically.
- Concurrency and idempotency guarantees stated in method names and proven by contract tests.

## 2. Structure

```text
persistence/                   (under the package root)
  ports/          interface types only: UnitOfWork + one repository per entity; the typed failures
                  (ConcurrencyConflict, LeaseLost) and typed results (Created | Existing, Page). Imports domain types only
  <database>/     the persistence adapter package: the only package allowed to import the database driver or build SQL
    schema        the schema source of truth, one definition the migration tool is checked against
    uow           the unit of work over one connection and one transaction
    mappers/      row ↔ domain model, one module per entity (created with the first entity)
    repositories/ one module per repository, implementing its port
    notifier      wake-ups from the database, if the store supports them
  memory/         in-memory twins for unit tests (store, unit of work, repositories)
  migrations/     the migration tool's files, checked against the schema source of truth
tests/persistence/contracts/   one suite per repository, run against both implementations
```

The profile names the real directory and files (e.g. `postgres/` in the python-postgres profile) and lists what the scaffold ships. Mappers, repository modules and contract suites arrive with the first entity (§7).

## 3. Interfaces

Language-neutral sketch; the profile has the code.

| Interface | Members | Guarantee |
| --- | --- | --- |
| `UnitOfWork` | one read-only accessor per repository; enter and exit a scope; `commit()`; `rollback()` | Leaving the scope without `commit()` rolls back, including on exceptions. Only the unit of work commits |
| `UnitOfWorkFactory` | `() -> UnitOfWork` | Injected by the composition root; a use case opens one per action |
| `OrderRepository` (example entity) | `add(order) -> Created | Existing` | Idempotent insert: a second call with the same idempotency key returns `Existing` with the stored row, never raises |
| | `get(order_id) -> Order | none` | Read by id |
| | `save(order, expected_version)` | Persist and bump the version; raises `ConcurrencyConflict` if the version moved |
| | `claim_due(now, limit) -> list` | Claim up to `limit` due rows with the store's atomic claim primitive; safe across processes |
| | `list_*(…, limit) -> Page` | Bounded; keyset pagination with a cursor |

Usage shape, in any language:

```text
with uow_factory() as uow:
    order = uow.orders.get(order_id)
    ...
    uow.orders.save(order, expected_version=order.version)
    uow.outbox.enqueue(message)
    uow.commit()            # only the unit of work commits
```

## 4. Rules

| # | Rule | Enforced by |
| --- | --- | --- |
| R1 | Only the persistence adapter package imports the database driver or builds SQL. No SQL strings anywhere else. | Layer-contract tool, SQL-location guard |
| R2 | Code outside `persistence/` depends only on `persistence/ports`. Only the composition root picks an implementation. | Layer-contract tool |
| R3 | One repository per entity (or per aggregate when rows are always written together). No generic `query(filters)`. | Review |
| R4 | Domain models in and out. Rows and ORM objects never leave the persistence adapter package; mappers translate. | Type checker + review |
| R5 | Repositories never commit. The caller owns the transaction. | `commit` exists only on `UnitOfWork` |
| R6 | No business logic in repositories (no retries, no decisions). Data invariants (uniqueness, version checks) are fine. | Review |
| R7 | Repositories never call each other. Cross-entity work belongs to the caller inside one unit of work. | Review |
| R8 | Concurrency is explicit: version checks raise `ConcurrencyConflict` / `LeaseLost`; claims are `claim_*` methods using the store's atomic claim primitive (e.g. `FOR UPDATE SKIP LOCKED` in Postgres). | Contract tests |
| R9 | Idempotent inserts return `Created(x)` / `Existing(x)` instead of raising. | Contract tests |
| R10 | Every list method takes a required `limit`; long lists use keyset pagination (`Page` with a cursor). | Signatures |
| R11 | Every port has a real database implementation and a memory implementation, and one shared contract suite both pass. | The repository guard in `check` |
| R12 | `now` is a parameter; never the database's own clock evaluated silently inside a query. | Frozen-clock contract tests |
| R13 | PII fields are mapped in one place (the mapper), so encryption or tokenization later touches only mappers. | Review |
| R14 | Schema change = the schema source of truth + a migration + mapper + memory twin + contract suite + `database-schema.md`. | `migrations-check` |
| R15 | Core tables are generic: no tenant, customer, or business-flow words in table, column, or repository names (`tenant_id` is the allowed exception). | Domain-word guard |

## 5. Memory twins

- Snapshot isolation: a row changed by two concurrent units of work fails the second commit with `ConcurrencyConflict`.
- Where the database resolves a race per statement (atomic claims, insert-or-return-existing), the twin emulates the database's outcome so the shared contract suite passes: a row locked by another live transaction is skipped by claims, counts as held for leases, and makes a racing idempotent insert raise `ConcurrencyConflict`.
- Twins need not enforce foreign keys; say so in the twin's documentation comment.

## 6. Testing

- **Contract suites** (one file per port in the contract-suite directory): a backend fixture runs each test against the real database (throwaway container, migrated to head, truncated after each test) and against memory. Cover the normal path, duplicates (`Existing`), version conflicts, lease expiry, `claim_*` exclusivity under concurrency, pagination, frozen time.
- **Unit tests** of use cases use memory implementations.
- **Integration and end-to-end tests** use the real database.
- **Completeness:** the repository guard fails when a repository port lacks a database implementation, a memory implementation or a contract suite; a test fails when `UnitOfWork` lacks the accessor.
- **Migrations:** a test migrates an empty throwaway database to head, then runs `migrations-check`.

## 7. Adding or changing an entity

1. Update `implementation/database-schema.md` (DDL, access pattern → index, migration number) and the repository catalog if the project keeps one.
2. Port method(s) named by intent, with concurrency and idempotency guarantees in the documentation comment.
3. The schema source of truth + a migration (forward-only; expand then contract for existing tables).
4. Mapper, database repository, memory twin.
5. Contract tests for the cases in §6.
6. Change record listing the migration and the repository methods added.
