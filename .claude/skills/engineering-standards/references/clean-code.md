# Clean code conventions (Python 3.12)

## Contents
1. Naming
2. Functions and modules
3. Types and data
4. Errors
5. Async and I/O
6. Comments and docstrings
7. Logging and tracing
8. Configuration and secrets
9. Dependencies

## 1. Naming

- Use the project vocabulary (`GLOSSARY.md`), the requirement terms from the phase docs, and the table names from `database-schema.md`. One concept, one name, everywhere.
- Names say what, not how: `acquire_lease`, `claim_due`, `list_pending` — not `do_update`, `process`, `handle_data`.
- Booleans read as questions: `is_fresh`, `has_open_wait`. Collections are plural. Units in names when ambiguous: `timeout_s`, `latency_ms`.
- No abbreviations beyond the well-known (`id`, `ctx`, `uow`).

## 2. Functions and modules

- One module, one purpose; aim for ≤ 300 lines. One handler per file; one integration per package; one repository per module.
- Functions do one thing at one level of abstraction; ≤ ~40 lines is a good signal, not a law. Extract when a comment would otherwise explain a block.
- Prefer pure functions for logic; keep I/O at the edges.
- Keyword-only arguments for anything beyond two parameters or any boolean flag.
- No hidden side effects: a function named `get_…` doesn't write.

## 3. Types and data

- `mypy --strict` clean. No `Any` in public signatures; no untyped `dict` across module boundaries.
- Pydantic v2 models for boundaries (API, file formats, integration I/O, model output); frozen dataclasses or Pydantic for domain values.
- Discriminated unions (`Annotated[..., Field(discriminator="type")]`) for variants; exhaustive `match` with `assert_never`.
- Money and units are `Decimal`; time is timezone-aware UTC `datetime`; durations are `timedelta`.
- IDs are typed (`NewType("OrderId", UUID)`), UUIDv7.

## 4. Errors

- Integration edges return values: a typed result (success | failure with category), typed model failures, `Created | Existing`.
- Raise for programmer errors and infrastructure faults; use the project's exception hierarchy (`domain/errors.py`; persistence failures in `persistence/ports/errors.py`), never bare `Exception`.
- Never swallow: no `except Exception: pass`, no returning `None` to mean "failed".
- Error messages say what happened and what to do; include IDs, never secrets or PII.

## 5. Async and I/O

- Async end to end for I/O (FastAPI, httpx, psycopg async). No blocking calls in async code; offload CPU-heavy work explicitly.
- Every external call has a timeout; timeouts come from configuration per operation, not literals scattered in code.
- Concurrency with `asyncio.TaskGroup` or a bounded pool; no fire-and-forget tasks without supervision.
- Retries only where the operation's policy allows (reads, transient errors); never around writes (use the recorded-intent protocol).

## 6. Comments and docstrings

- Comments explain **why** (a constraint, a requirement, a non-obvious trade-off), never restate the code.
- Tag requirement-driven code with its ID: `# OR-12: an order is charged at most once`.
- Public functions, ports, and repository methods get docstrings stating guarantees (idempotency, concurrency, what raises).
- **No change-history comments in code** ("fixed by X on date", "old version below"): history lives in change records and git.
- No commented-out code; delete it.
- `TODO` only with a tracked follow-up id from a ledger: `# TODO(P04-F2): …`.

## 7. Logging and tracing

- structlog via `get_logger(__name__)` from `observability/logging.py`; console renderer locally, JSON in deployed environments (the `LOGGING__FORMAT=json` setting under the project's env prefix).
- Bind correlation IDs (request, aggregate, job, external call) with a context helper so every event carries them.
- Module loggers are `log = get_logger(__name__)` at import and stay lazy; don't build a bound logger at module level (it freezes configuration). Bind extra context inside functions.
- Log events, not prose: `log.info("order.placed", order_id=..., total=...)`.
- Never log secrets, tokens, or PII (phone numbers, emails, message content, payloads); redaction happens in mappers and adapters.
- When tracing is enabled: one span per request, use case, external call, model call, and background job, carrying the same IDs.

## 8. Configuration and secrets

- All settings in `settings.py` at the package root (pydantic-settings, the project's env prefix, nested with `__`); passed via the container.
- Secrets only from environment or a secret store; never committed (`.env` is in `.gitignore`), never in fixtures, logs, or audit payloads.
- Tunable business values belong in data or configuration owned by the business, not core settings.

## 9. Dependencies

- Add a dependency only with a reason in the change record; prefer the standard library and what's already in the stack.
- Pin via `uv.lock`. New vendor SDKs go behind a port (ADR if it's a new category of vendor).
