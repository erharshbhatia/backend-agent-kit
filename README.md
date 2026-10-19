# backend-agent-kit

A starting point for building backend services with Claude Code and many agents working in parallel. It packages the way we work: from a tech doc, to implementation plans, to phased builds tracked in ledgers, with every change documented and every agent held to the same standards.

Nothing in here is specific to one product. You copy the kit, fill in the placeholders, and write your own tech doc.

## What's inside

| Path | What it is |
| --- | --- |
| `CLAUDE.md` | Rules every agent follows in the new project (fill in the `<...>` placeholders) |
| `.claude/skills/` | The process, as skills Claude Code loads automatically |
| `scaffold/python-service/` | A small, runnable Python service skeleton with the tooling the standards expect |
| `docs/` | Empty ledgers and indexes: workstreams (including `HANDOFF.md`, the resume point), change records, decisions |
| `CHANGELOG.md` | What changed in the kit, so projects bootstrapped earlier can pull improvements |
| `implementation/` | Where the parent plan, outcome docs and phase docs go |

### Skills

| Skill | Use it for |
| --- | --- |
| `project-bootstrap` | Starting a new project from this kit: placeholders, first docs, first ADRs, the P00 foundations phase |
| `tech-doc-writing` | Writing and evolving the HLD (`tech-doc.md`): requirements, estimates, architecture, decisions, open questions |
| `implementation-planning` | Turning the HLD into a parent plan, binding specs, an outcome doc and phase docs |
| `project-guide` | Orientation at the start of every task: index of docs, invariants, architecture, glossary, debugging |
| `sdlc-workflow` | The lifecycle for every change: orient → intake → design note → plan → build → verify → review → document → close |
| `engineering-standards` | Hexagonal layers, repository + unit of work, registries, typed contracts, clean code, testing, review checklist |
| `change-records` | One change record per change, ADRs for decisions, commit format, comment rules, docs stay true |
| `workstream-tracking` | STATUS, per-phase ledgers, open decisions, claiming tasks, handoffs |
| `multi-agent-development` | Running parallel agents: worktrees, file ownership, throwaway resources, integration, review and audit subagents |

## How a project flows

```text
business inputs (briefs, flows, PDFs)        test cases, not specs
        │  tech-doc-writing
        ▼
tech-doc.md (HLD)                            requirements, estimates, architecture, decisions
        │  implementation-planning
        ▼
implementation/00-implementation-plan.md     scope, requirement IDs, stack, layout, interfaces
implementation/<spec>.md                     binding specs (schema, data access, formats)
implementation/outcome-01-<slug>.md          what to build now: the slice of each phase, milestones
implementation/pNN-<slug>.md                 one doc per phase, with Decisions to review
        │  workstream-tracking
        ▼
docs/workstreams/STATUS.md + PNN-*.md        who is doing what, decisions, blockers, handoffs
        │  sdlc-workflow + engineering-standards (+ multi-agent-development)
        ▼
code + tests + docs/changes/* + docs/decisions/*
```

## Start a new project

1. Copy the kit into a new folder and start git there:
   ```bash
   cp -R backend-agent-kit my-service && cd my-service && rm -rf .git && git init
   ```
2. Open Claude Code in the new folder and ask: "bootstrap this project from the kit". The `project-bootstrap` skill walks through placeholders, the tech doc, the plans and the P00 foundations phase.
3. Copy `scaffold/python-service/` to the repository root (or into a package folder) when P00 starts, and rename the `app` package.

## Defaults you can change

The default stack is Python 3.12, uv, FastAPI, SQLAlchemy async with psycopg 3, Alembic, Pydantic v2, structlog, pytest with Hypothesis and testcontainers, ruff, mypy `--strict` and import-linter. `make check` runs every gate that needs no Docker; `make check-all` adds the Postgres tests and `alembic check`. Record a different choice as an ADR in the new project; the process skills don't depend on the stack.

`docs/` is tracked in git by default. If a project keeps docs elsewhere, record that as an ADR and update `change-records` and `workstream-tracking`.

## Updating a project from a newer kit

The seven process skills (`engineering-standards`, `sdlc-workflow`, `change-records`, `workstream-tracking`, `multi-agent-development`, `implementation-planning`, `tech-doc-writing`) contain nothing project-specific, so a project can copy newer versions straight over its own. `project-bootstrap` ("Generic files stay generic") has the recipe; `CHANGELOG.md` lists what each kit change needs on the project side.
