---
name: project-bootstrap
description: How to start a new backend project from this kit — copy it, fill every placeholder, write the project's product, glossary and invariants, write the tech doc, derive the implementation plan, outcome and phase docs, create the ledgers, record the first ADRs, and build the P00 foundations phase from scaffold/python-service. Use when the owner says "start a new project", "set up a repo from the kit", "bootstrap", "initialize the project", or when a repo from this kit still contains `<Project>`-style placeholders.
---

# Project bootstrap

The kit gives a new project our whole way of working on day one: the lifecycle, the standards, the ledger, change records, multi-agent rules, and a starter service that already enforces the standards. Bootstrapping turns the generic kit into this project's kit. Do it in order; each step feeds the next.

## Order

| # | Step | Produces | Skill |
| --- | --- | --- | --- |
| 1 | Copy the kit and fill placeholders | A repo with no `<…>` tokens left in process files | this one |
| 2 | Write product, glossary, invariants | `project-guide/knowledge/{PRODUCT,GLOSSARY,INVARIANTS}.md` | `project-guide` |
| 3 | Write the tech doc (HLD) | `tech-doc.md` (+ optional `docs/site/hld.html`) | `tech-doc-writing` |
| 4 | Plan the build | `implementation/00-implementation-plan.md`, `outcome-01-<slug>.md`, `pNN-<slug>.md`, `implementation/README.md` | `implementation-planning` |
| 5 | Record the first decisions | ADR-0001… (below) | `change-records` |
| 6 | Create the ledgers | `docs/workstreams/STATUS.md`, `OPEN-DECISIONS.md`, `ADHOC.md`, `P00-foundations.md` | `workstream-tracking` |
| 7 | Build P00 foundations | The service skeleton, green `make check` | `sdlc-workflow`, `engineering-standards` |
| 8 | Start phase work | Waves of tasks | `multi-agent-development` |

Ask the owner for decisions in **one** batch at step 2–3 (product goals, non-goals, stack deviations, LLM test policy, docs in git). Everything else you do without asking.

## 1. Copy and fill placeholders

```bash
cp -R <kit>/ <new-repo>/ && cd <new-repo>
git init
```

Keep `.claude/skills/`, `CLAUDE.md`, `docs/`, `implementation/` (templates), and `scaffold/` (until P00 has copied what it needs, then delete `scaffold/`).

Find every placeholder: `grep -rnE '<(Project|package|PREFIX|domain-words|outcome|retired terms|vendor)>' --include='*.md' --include='*.toml' --include='*.yml' --include='*.py' .`

| Placeholder | Meaning | Where it appears |
| --- | --- | --- |
| `<Project>` | Human name of the project | `CLAUDE.md`, `project-guide/SKILL.md`, tech doc and plan templates, scaffold `pyproject.toml` descriptions and docstrings |
| `<package>` | Python package name (snake_case) | `CLAUDE.md`, `engineering-standards` references, `project-guide/knowledge/*`, plan templates (the scaffold itself uses `app`; see renames below) |
| `<PREFIX>` | Environment variable prefix (e.g. `ORD`) | `engineering-standards/references/clean-code.md`, `project-guide/knowledge/INDEX.md`, parent-plan template (the scaffold uses `APP_`) |
| `<domain-words>` | Words generic code must never contain (tenant, customer, workflow names) | `CLAUDE.md`, `engineering-standards` rule 9, `project-guide/knowledge/INVARIANTS.md`; also fill `scripts/guards.toml` `forbidden_words` |
| `<outcome>` | An outcome name, used in ledger rows as `not started (deferred: <outcome>)` | `sdlc-workflow`, `workstream-tracking`, `implementation-planning` (filled per row, not at bootstrap) |
| `<retired terms>` | Words the team agreed not to use as system terms | `CLAUDE.md` "Never"; list them in `GLOSSARY.md` "Retired terms" |
| `<vendor>` | External SDKs that must live behind a port (LLM, payments, queues) | `engineering-standards/references/lld.md`; add one `.importlinter` contract per vendor |

Scaffold renames (when P00 copies it in):

| In the scaffold | Rename to |
| --- | --- |
| directory `app/` and `app/src/app/` | `<package>/` and `<package>/src/<package>/` |
| `app.` in imports, `.importlinter`, `pyproject.toml`, `alembic.ini`, `scripts/guards.toml`, `Dockerfile`, `docker-compose.yml` | `<package>.` |
| `APP_` env prefix in `settings.py`, `.env.example`, `docker-compose.yml` | `<PREFIX>_` |
| `appctl` console script | your CLI name |
| schema `app` in `tables.py` and `0001_baseline.py` | your schema name |
| `app-workspace`, compose project `app`, image `app-python:local` | project names |

After renaming: `grep -rn '\bapp\b\|APP_\|appctl' <package> scripts tests *.toml *.yml Dockerfile Makefile .importlinter alembic.ini` should only show intended hits.

## 2. Product, glossary, invariants

- `PRODUCT.md`: what we're building, for whom, goals with numbers, non-goals, requirement-ID prefixes, the current outcome.
- `GLOSSARY.md`: one concept, one name. Include the retired terms and what replaced them.
- `INVARIANTS.md`: keep the kit's generic invariants (layers, repositories, injected time and ids, idempotent boundaries, no secrets, process rules); add the project's product and safety invariants. Each invariant is one sentence a reviewer can check.

## 3–4. Tech doc and plan

Follow `tech-doc-writing`, then `implementation-planning`. The plan must name P00 foundations as the first phase and the first outcome's slice of every phase.

## 5. First ADRs

| ADR | Decision | Notes |
| --- | --- | --- |
| ADR-0001 | Adopt this kit's process (lifecycle, ledger, change records, multi-agent rules) | Accepted at bootstrap |
| ADR-0002 | Stack: language, framework, database, migration tool, test tools | Default: the scaffold's stack. Record deviations |
| ADR-0003 | Testing policy for external services (LLMs, payment APIs) | Options: real calls in tests marked `external` (fail, not skip, without a key); recorded fixtures; fakes. State which and why |
| ADR-0004 | Docs in git | Default: `docs/` tracked. If the owner keeps docs local, record it and update `.gitignore` |
| ADR-0005 | Local environment: compose stack, ports, dev database rules | Name the dev database agents must never touch |

## 6. Ledgers

Create from `workstream-tracking/assets/`. `STATUS.md` names the current outcome and lists every phase. `P00-foundations.md` gets the checklist below as its task list.

## 7. P00 foundations checklist

| Id | Task | Done when |
| --- | --- | --- |
| P00-T1 | `git init`, `.gitignore` (secrets, caches, `.claude/worktrees/`), first commit only when the owner asks | `.env` is ignored; `git status` clean of secrets |
| P00-T2 | Copy `scaffold/python-service/` into the repo root; rename package, prefix, CLI, schema | Grep for `app`/`APP_` shows only intended hits |
| P00-T3 | `uv sync`; commit `uv.lock` with the code | `uv run python -c "import <package>"` works |
| P00-T4 | Settings: database, logging, worker; `.env.example` with no secrets | Settings load from env and `.env` |
| P00-T5 | Domain basics: `Clock`, `IdGenerator`, typed ids, error hierarchy | Unit tests green |
| P00-T6 | Persistence: `Database` and `UnitOfWork` ports, Postgres and memory units of work, Alembic baseline, contract-suite harness | `make up && make migrate && make migrations-check` green |
| P00-T7 | Composition root: frozen `Container`; API (`/livez`, `/readyz`), worker loop, CLI | `make stack` healthy |
| P00-T8 | Guards: import-linter contracts, domain words (`guards.toml`), SQL location, repository completeness, ruff banned APIs | `make check` green; a deliberate violation fails each guard |
| P00-T9 | Logging: structlog, JSON in containers, trace ids bound per request | One request produces one structured line with ids |
| P00-T10 | Docs: `project-guide/knowledge/INDEX.md` lists every doc and command; P00 "As built" section; change record | Next agent can run everything from the docs |

Exit: `make check` and `make check-all` green with output pasted into the P00 change record; an independent review subagent found no must-fix issues.

## 8. Start phase work

Resolve the next phases' "Decisions to review" in one batch, then plan waves with `multi-agent-development`.
