# Testing

Language-neutral. Tool names per stack are in `stacks/<profile>.md`; concrete commands in `project-guide/knowledge/STACK.md`.

## Pyramid

| Layer | What | Profile tools | Uses |
| --- | --- | --- | --- |
| Domain | Pure logic: rules, policies, validation, `UNKNOWN` semantics, arithmetic | unit runner, property-based testing | No I/O at all |
| Handlers | One handler per test module with a fake context | unit runner | Fakes |
| Application | Use cases | unit runner | Memory repositories, fake integrations, the mock of each outside system |
| Runtime | State-machine tests: interleaved requests, events, timers, crashes, duplicates; the invariants | stateful property-based testing | Memory repositories (many runs) + the real database (fewer runs) |
| Contracts | Every repository port against both implementations; every adapter against its conformance suite; integrations against the mock | parameterized runner | Throwaway database container, local mock servers, HTTP mocking |
| End-to-end | Scenarios through the real entrypoints | runner or a scenario runner | Real app, real database, mocked outside systems, frozen clock |
| Model quality (if any) | Evals on labelled sets | eval harness | Per the model test-policy ADR |

The profile names the actual tool for each row.

## Rules

- **Write the failing test first** for bugs (reproduce, then fix) and for new behaviour where the shape is clear.
- **Test at the lowest layer that can prove the behaviour.** Do not use an end-to-end scenario to test a pure function.
- **Deterministic by construction:** a frozen clock, seeded IDs, memory repositories, mock servers, HTTP mocking. A flaky test is a bug; fix it or quarantine it with a tracked follow-up, never retry it into passing.
- **Models follow one policy, chosen by ADR.** Either real calls (tests tagged `external`, fail rather than skip without the key, assert outcomes not wording) or recorded fixtures with a refresh procedure. Never mix silently.
- **Name tests after behaviour:** `place_order_twice_returns_existing`, not `place_order_2`.
- **Trace requirements:** requirement and scenario IDs appear in test names or documentation comments.
- **Invariants get property tests:** idempotency, one writer, no lost event, no step run twice.
- **No real network in tests** except what the model policy allows. Outside systems are always mocked.
- **Never test against a shared or developer database.** Use a throwaway container per run or per agent.
- **Coverage is a signal, not a target;** new code paths for writes, leases, dedupe, and failure categories must be covered.

## Tags

Two reserved tags every profile implements: `db` (needs the real database in a throwaway container) and `external` (reaches a real outside service; policy in an ADR). The runner rejects unknown tags. Untagged tests must run with no Docker and no network.

## Commands

Abstract names; `project-guide/knowledge/STACK.md` gives the concrete command for each (the python-postgres scaffold ships them as Makefile targets).

| Command | Runs |
| --- | --- |
| `check` | Lint, format check, types, layer contracts, guards, and every test not tagged `db` or `external` (no Docker, no keys) |
| `test` | The tests `check` runs, alone |
| `test-db` | Tests tagged `db`: repository contract suites and other database tests (throwaway container; needs Docker) |
| `migrations-check` | The schema source of truth and the migrations agree |
| `check-all` | `check` + `test-db` + `migrations-check` |
| `test-external` | Tests tagged `external` (real outside services; needs keys and the test-policy ADR). Passes while none exist |
| `e2e` | End-to-end scenarios in the scenarios directory, one module per scenario id. The scaffold ships S0 (the service boots and answers); scenarios that use the database are tagged `db` and need Docker |

Projects add their own and list them in `project-guide/knowledge/INDEX.md` and `STACK.md`: `eval` for model evals against labelled sets, UI checks, scenario runners.
