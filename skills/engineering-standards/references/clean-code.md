# Clean code conventions

Language-neutral. The stack profile (`stacks/<profile>.md`) says how each convention is spelled in the project's language and which tool enforces it; `project-guide/knowledge/STACK.md` names the tools and files.

## Contents
1. Naming
2. Functions and modules
3. Types and data
4. Errors
5. Async and I/O
6. Comments and documentation
7. Logging and tracing
8. Configuration and secrets
9. Dependencies

## 1. Naming

- Use the project vocabulary (`GLOSSARY.md`), the requirement terms from the phase docs, and the table names from `database-schema.md`. One concept, one name, everywhere.
- Names say what, not how: `acquire_lease`, `claim_due`, `list_pending`, not `do_update`, `process`, `handle_data`.
- Booleans read as questions: `is_fresh`, `has_open_wait`. Collections are plural. Units in names when ambiguous: `timeout_s`, `latency_ms`.
- No abbreviations beyond the well-known (`id`, `ctx`, `uow`).

## 2. Functions and modules

- One module, one purpose; aim for 300 lines or fewer. One handler per file; one integration per package; one repository per module.
- Functions do one thing at one level of abstraction; about 40 lines is a good signal, not a law. Extract when a comment would otherwise explain a block.
- Prefer pure functions for logic; keep I/O at the edges.
- Named arguments for anything beyond two parameters or any boolean flag where the language has them; otherwise an options object.
- No hidden side effects: a function named `get_…` does not write.

## 3. Types and data

- The type checker runs in its strictest mode and passes. No "any" type in public signatures; no untyped map or dictionary across module boundaries.
- Typed boundary models (validated, serializable) for everything that crosses a boundary: API, file formats, integration I/O, model output. Domain values are immutable typed records.
- Variants are discriminated unions with a tag field; matching on them is exhaustive and the type checker proves it.
- Money and units are a decimal type, never floats; time is timezone-aware UTC; durations are a duration type, not bare numbers.
- IDs are distinct types per entity, not bare strings; values are time-ordered unique ids (e.g. UUIDv7).

## 4. Errors

- Integration edges return values: a typed result (success | failure with category), typed model failures, `Created | Existing`.
- Raise or throw for programmer errors and infrastructure faults; use the project's error hierarchy (domain errors in `domain/`, persistence failures in `persistence/ports/`), never the language's base exception type.
- Never swallow: no catch-all that ignores, no returning null to mean "failed".
- Error messages say what happened and what to do; include IDs, never secrets or PII.

## 5. Async and I/O

- Non-blocking I/O end to end where the stack is async; no blocking calls on the event loop; offload CPU-heavy work explicitly.
- Every external call has a timeout; timeouts come from configuration per operation, not literals scattered in code.
- Concurrency through a structured primitive (a task group or a bounded pool) whose failures propagate; no fire-and-forget tasks without supervision.
- Retries only where the operation's policy allows (reads, transient errors); never around writes (use the recorded-intent protocol).

## 6. Comments and documentation

- Comments explain **why** (a constraint, a requirement, a non-obvious trade-off), never restate the code.
- Tag requirement-driven code with its ID in a comment: `OR-12: an order is charged at most once`.
- Public functions, ports, and repository methods get documentation comments stating guarantees (idempotency, concurrency, what raises).
- **No change-history comments in code** ("fixed by X on date", "old version below"): history lives in change records and git.
- No commented-out code; delete it.
- `TODO` only with a tracked follow-up id from a ledger: `TODO(P04-F2): …`.

## 7. Logging and tracing

- Structured key-value logging through the project's logging module; a human-readable renderer locally, JSON in deployed environments, switched by a setting.
- Bind correlation IDs (request, aggregate, job, external call) with a context helper so every event carries them.
- Module loggers are created at import and stay lazy; do not bind context at module level (it freezes configuration). Bind extra context inside functions.
- Log events, not prose: an event name such as `order.placed` with fields `order_id` and `total`.
- Never log secrets, tokens, or PII (phone numbers, emails, message content, payloads); redaction happens in mappers and adapters.
- When tracing is enabled: one span per request, use case, external call, model call, and background job, carrying the same IDs.

## 8. Configuration and secrets

- All settings in the settings module: typed, loaded from the environment under the project's prefix, nested keys supported; passed via the container. It is the only module that reads the environment (the banned-API tool enforces this).
- Secrets only from environment or a secret store; never committed (`.env` is git-ignored), never in fixtures, logs, or audit payloads.
- Tunable business values belong in data or configuration owned by the business, not core settings.

## 9. Dependencies

- Add a dependency only with a reason in the change record; prefer the standard library and what is already in the stack.
- Pin via the lock file; regenerate it with `deps-lock`, never edit it by hand. New vendor SDKs go behind a port (ADR if it is a new category of vendor).
