# Index: where everything lives

<!-- Fill-in template. `project-bootstrap` creates the first version; every change that adds, moves or retires a doc updates it. Keep one row per document. -->

## Design documents

| Path | What it is | Authoritative for |
| --- | --- | --- |
| `tech-doc.md` | HLD (see `tech-doc-writing`) | Problem, goals, architecture, estimates, alternatives, open questions |
| `docs/site/hld.html` | Optional published HLD page (URL: <hld-page-url>) | Must mirror `tech-doc.md`; republished on every HLD change |
| `implementation/README.md` | Phase index and schedule | Phase order and dependencies |
| `implementation/00-implementation-plan.md` | Parent build plan (see `implementation-planning`) | Scope, requirement IDs, stack, repo layout, core interfaces, test strategy, milestones |
| `implementation/outcome-NN-<slug>.md` | **Current outcome** | What is built now, the slice of each phase, milestone order, acceptance scenarios, what is deferred |
| `implementation/pNN-<slug>.md` | One plan per phase | Scope, files, design details, tasks, tests, exit criteria, decisions to review, "As built" |
| `implementation/database-schema.md` | Binding spec: full DDL and rationale | Tables, constraints, indexes, migrations |
| `implementation/repository-pattern.md` | Optional binding spec: data-access standard | Repositories, unit of work, rules R1–R15 (the generic version is in `engineering-standards/references/repository.md`) |
| `implementation/<other-spec>.md` | <API spec, file format, protocol> | <what it binds> |

## Process documents (created and maintained by agents)

| Path | What it is | Maintained by skill |
| --- | --- | --- |
| `docs/workstreams/STATUS.md` | Current outcome and one-line status of every phase | `workstream-tracking` |
| `docs/workstreams/PNN-*.md` | Per-phase ledger: tasks, decisions, blockers, session log | `workstream-tracking` |
| `docs/workstreams/OPEN-DECISIONS.md` | Every "Decision to review" across phases | `workstream-tracking` |
| `docs/workstreams/ADHOC.md` | Work outside a single active phase | `workstream-tracking` |
| `docs/workstreams/HANDOFF.md` | Resume point: read first in a new session | `workstream-tracking` |
| `docs/changes/INDEX.md` + `docs/changes/YYYY/*.md` | One change record per change | `change-records` |
| `docs/decisions/INDEX.md` + `docs/decisions/ADR-*.md` | Architecture decision records | `change-records` |

## Business inputs (test cases, not specs)

<!-- Source documents from the business: BRDs, flow PDFs, API handovers. They are inputs the design was derived from; the design docs above win. -->

| File | Used by |
| --- | --- |
| <input-file> | <phase, requirement prefix> |

## Superseded decisions

<!-- ADRs kept for history only, with the ADR that replaced them. -->

## Archived (do not use for decisions)

<!-- Old versions of the HLD or plans, e.g. `tech-doc-v1.md`. -->

## Code layout

<!-- Filled by `project-bootstrap`; keep it true. Default layout: -->

```text
<package>/src/<package>/
  entrypoints/      api (FastAPI), worker, cli — thin
  application/      use cases
  domain/           pure models and rules
  persistence/      ports/ (Protocols, errors, results), postgres/, memory/, migrations/
  observability/    logging (and tracing)
  <module>/         one package per capability that talks to the outside: port.py (Protocol)
                    + one adapter module per technology, e.g. models/, integrations/<partner>/
  bootstrap.py      composition root
  settings.py       pydantic-settings, env prefix <PREFIX>_
tests/              mirrors the package; scenarios/ for end-to-end; persistence/contracts/ for repository suites
docs/               workstreams, changes, decisions (tracked in git)
implementation/     plans and binding specs
```

Commands: `make up` (local Postgres), `make migrate`, `make check` (lint, format, types, import contracts, guards, tests not marked `db`/`external`; no Docker), `make test-db` (Postgres tests), `make migrations-check` (`alembic check`), `make check-all` (all three), `make e2e` (scenarios in `tests/scenarios/`), `make test-external` (tests marked `external`; needs keys), `make stack` (whole system in containers), <other commands>.

Kit version this project's generic skills match: <kit commit or CHANGELOG entry> (`project-bootstrap`, "Generic files stay generic").
