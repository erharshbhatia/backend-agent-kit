# Testing

## Pyramid

| Layer | What | Tools | Uses |
| --- | --- | --- | --- |
| Domain | Pure logic: rules, policies, validation, `UNKNOWN` semantics, arithmetic | pytest, Hypothesis | No I/O at all |
| Handlers | One handler per test module with a fake context | pytest | Fakes |
| Application | Use cases | pytest | Memory repositories, fake integrations, the mock of each outside system |
| Runtime | State-machine tests: interleaved requests, events, timers, crashes, duplicates; the invariants | Hypothesis stateful | Memory repositories (many runs) + Postgres (fewer runs) |
| Contracts | Every repository port against both implementations; every adapter against its conformance suite; integrations against the mock | pytest parameterized | Testcontainers Postgres, local mock servers, respx |
| End-to-end | Scenarios through the real entrypoints | pytest or a scenario runner | Real app, real Postgres, mocked outside systems, frozen clock |
| Model quality (if any) | Evals on labelled sets | eval harness | Per the model test-policy ADR |

## Rules

- **Write the failing test first** for bugs (reproduce, then fix) and for new behaviour where the shape is clear.
- **Test at the lowest layer that can prove the behaviour.** Don't use an end-to-end scenario to test a pure function.
- **Deterministic by construction:** `FrozenClock`, seeded IDs, memory repositories, mock servers, respx. A flaky test is a bug; fix it or quarantine it with a tracked follow-up, never retry it into passing.
- **Models follow one policy, chosen by ADR.** Either real calls (tests marked `external`, fail rather than skip without the key, assert outcomes not wording) or recorded fixtures with a refresh procedure. Never mix silently.
- **Name tests after behaviour:** `test_place_order_twice_returns_existing`, not `test_place_order_2`.
- **Trace requirements:** requirement and scenario IDs appear in test names or docstrings.
- **Invariants get property tests:** idempotency, one writer, no lost event, no step run twice.
- **No real network in tests** except what the model policy allows. Outside systems are always mocked.
- **Never test against a shared or developer database.** Use testcontainers or a per-agent throwaway container.
- **Coverage is a signal, not a target;** new code paths for writes, leases, dedupe, and failure categories must be covered.

## Markers

The scaffold registers two pytest markers (`--strict-markers`): `db` (needs a Postgres testcontainer) and `external` (reaches a real outside service; policy in an ADR). Unmarked tests must run with no Docker and no network.

## Commands

Shipped by the scaffold's `Makefile`:

| Command | Runs |
| --- | --- |
| `make check` | Lint, format check, types, import-linter, guards, and every test not marked `db` or `external` (no Docker, no keys) |
| `make test` | pytest excluding `db` and `external` tests |
| `make test-db` | Tests marked `db`: repository contract suites and other Postgres tests (testcontainers; needs Docker) |
| `make migrations-check` | `alembic check`: `tables.py` and migrations agree (after `make up && make migrate`) |
| `make check-all` | `make check` + `make test-db` + `make migrations-check` |
| `make test-external` | Tests marked `external` (real outside services, e.g. an LLM API; needs keys and the test-policy ADR). Passes while none exist |
| `make e2e` | End-to-end scenarios in `tests/scenarios/`, one module per scenario id. The scaffold ships S0 (the service boots and answers); scenarios that use Postgres are marked `db` and need Docker |

Projects add their own and list them in `project-guide/knowledge/INDEX.md`: `make eval` for model evals against labelled sets, UI checks, scenario runners.
