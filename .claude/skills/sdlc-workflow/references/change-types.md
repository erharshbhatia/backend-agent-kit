# Change types and what each requires

Pick the most specific type; a change can have several (e.g. `feature` + `schema`). The strictest column wins.

| Type | Examples | Design note | ADR | Owner approval before build | Extra verification | Docs to update |
| --- | --- | --- | --- | --- | --- | --- |
| `phase-task` | A task from a phase doc | Yes | If it deviates from the phase doc | If it deviates from the phase doc | Phase exit criteria it covers | Phase doc "As built" if behaviour differs |
| `feature` | New capability not in a phase doc | Yes | If it adds/changes an interface | **Yes** | Contract + end-to-end scenario tests | Parent plan or a new phase doc; HLD if architectural |
| `bugfix` | Wrong behaviour | Short (cause + fix) | No (unless the fix changes a decision) | No | Failing test first, then green | `DEBUGGING.md` if it's a new failure pattern |
| `integration` | New or changed call to an outside system (connector, partner API, webhook source) | Yes (contract, read vs write, timeouts, retries, idempotency, reconcile) | If an assumed contract replaces a real one or vice versa | Assumed contracts: **yes** | Contract tests against the mock; failure categories; signature tests for webhooks | Integration catalog in the parent plan; mock routes |
| `schema` | Table/column/index/migration | Yes (access pattern → index) | If it changes the data model contract | **Yes** | `make check-all`: repository contract suites (both implementations), `alembic upgrade head` + `alembic check` | `database-schema.md`, repository catalog |
| `runtime` | Background workers, leases, timers, queues, recovery, concurrency | Yes | If semantics change | **Yes** | Property/state-machine tests, crash and duplicate scenarios | Phase doc, HLD runtime section, `ARCHITECTURE.md` |
| `interface` | Change to a published port, API, event, or file format | Yes | **Yes** | **Yes** | Every adapter's conformance suite; API compatibility | The spec doc for that interface |
| `model` | Model choice, prompts, safety settings, AI SDK | Yes | Vendor/SDK change: **yes** | **Yes** | Eval suite before/after with numbers | Model section of the HLD and phase doc |
| `dependency` | Add/upgrade a library | Short (why, alternatives) | New category of dependency | Major version / new category: **yes** | Full `make check` | Parent plan stack section if the stack changes |
| `refactor` | No behaviour change | Short (why, boundaries) | No | Cross-module: **yes** | Full `make check`; no test changes except moves | Only if structure docs mention moved code |
| `security-sensitive` | Auth, secrets, PII handling, webhook signatures, access policy | Yes | Often | **Yes** | Negative tests (bad signature, missing auth, wrong tenant), independent review | HLD security section, phase doc |
| `config` | A default or parameter value in docs or settings | Short | If the value is fixed by an accepted ADR: a superseding ADR citing the owner's instruction | No, when the owner asked for it | Tests of affected behaviour | Every copy found by grep, including published pages |
| `docs-only` | Clarify or fix docs | No | No | No | Links resolve; no contradictions introduced | The docs themselves |

<!-- Projects add their own types here (e.g. a type for adding a workflow definition or a new handler kind), with the same columns. -->

## Notes

- **"Approval" means:** show the owner the design note (and ADR if any) and get an explicit go-ahead before Stage 4. Record who approved and when in the change record.
- **A phase task that simply follows its phase doc** needs no extra approval: the phase doc's decisions are the approval, once its "Decisions to review" are resolved.
- **Work with no phase doc:** the design lives in the change record; add new requirement IDs with a new prefix to the parent plan's requirements section. Ask for everything needing approval in one message.
- **Anything touching writes, leases, idempotency, money, or user-facing claims** is at least `runtime` or `feature` in scrutiny, whatever it's called.
