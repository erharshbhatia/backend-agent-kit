---
name: implementation-planning
description: How to turn the HLD (tech-doc.md) into an executable build plan for many agents — the parent implementation plan (scope, requirement IDs, stack, repo layout, core interfaces, testing strategy, milestones, extension recipes), binding specs (database schema, data-access standard, formats), an outcome doc that names the slice of each phase to build now and the milestone order, and small phase docs (goal, scope, files, design, tasks PNN-Tn, tests, exit criteria, "Decisions to review" that gate build, "As built" after build). Use after the tech doc is reviewed; when asked to "plan the implementation", "break this into phases", "write a phase doc", "what do we build first", "define the MVP / POC / next outcome", "add a phase", or "update the plan after building"; and when a built phase needs its "As built" section. Pairs with workstream-tracking (ledgers come from these docs) and sdlc-workflow (which executes them).
---

# Implementation planning

The HLD says what the system is. The plan says how many agents build it in small, verifiable pieces without stepping on each other, and in what order so that something runs early. Every phase doc becomes a ledger (`workstream-tracking`); every task in it is executed through `sdlc-workflow`.

## The documents

| File | Role | Template |
| --- | --- | --- |
| `implementation/README.md` | Index: current outcome, phase table (deps, estimates), parallelism chart, how to review a phase doc | `assets/implementation-readme-template.md` |
| `implementation/00-implementation-plan.md` | **Parent plan**: scope, requirements with IDs, stack, LLD principles, repo layout, core interfaces, testing strategy, milestones, extension recipes, open items | `assets/parent-plan-template.md` |
| `implementation/<spec>.md` | **Binding specs**: the contracts many phases share (database schema, data-access standard, file or API formats) | `assets/spec-template.md` |
| `implementation/outcome-NN-<slug>.md` | **Current outcome**: what is built now, the slice of each phase it needs, milestone order, acceptance scenarios, deferred items | `assets/outcome-template.md` |
| `implementation/pNN-<slug>.md` | **Phase docs**: one module or tightly related group each | `assets/phase-template.md` |

Authority when they disagree (also in `project-guide`): accepted ADR > binding spec > phase doc > parent plan > HLD. Fix the lower one, never silently pick.

## Step 1: Parent plan

Write it from the HLD:
1. **Scope**: in scope; out of scope as a table `Item | Why deferred | Hook left`. A hook (port, reserved field, interface) means deferring does not force a rewrite later.
2. **Requirements distilled from the inputs**: tables per area with `ID | Requirement | Source`. These IDs are the thread from business input to test.
3. **Stack**: language, framework, database, libraries, each with one line of why. The kit default (Python 3.12, uv, FastAPI, SQLAlchemy async + psycopg3, Alembic, Pydantic v2, structlog, pytest + Hypothesis + testcontainers, ruff, mypy --strict, import-linter) holds unless the HLD changes it by ADR.
4. **LLD principles and repo layout**: the layers and where code goes (`engineering-standards`), the package tree.
5. **Core interfaces**: the ports (Protocols) every phase codes against, written as signatures. Getting these right early is what lets phases run in parallel.
6. **Testing strategy**: the pyramid per layer, the scenario suite that proves the requirements (one scenario per business example, each with an ID).
7. **Milestones**: full-scope milestones with deliverables and exit criteria.
8. **Extension recipes**: `To add… | Touch only | Must not touch`. If a common extension touches core code, the design is not done.
9. **Open items and assumptions**: `# | Item | Assumption we build on | Needed from`.

## Step 2: Binding specs

Write a spec when a contract is shared by several phases and must not drift: the database schema (derived, not drawn: entities → access patterns → normalize → invariants as constraints → indexes from patterns → concurrency → volume and retention → privacy → migration order), the data-access standard (rules with IDs like `R1`–`Rn`), any file or wire format. Specs end with "Decisions to review" and are updated in the same change as the code that alters them.

## Step 3: Phases

Cut phases by module, not by layer: each phase owns a package or a tightly related group, has a clear dependency list, and is 1–2 weeks of work. Number them with two digits: `P00`, `P01`, … (files `p00-<slug>.md`, ledgers `P00-<slug>.md`). `P00` is always foundations (repo, tooling, `make check`, database baseline, bootstrap, settings, logging), built by `project-bootstrap`.

Each phase doc follows `assets/phase-template.md`:
- **Goal**, **In scope**, **Out of scope**.
- **Modules and files**: the exact paths it creates. This is also the ownership list for parallel agents.
- **Design details**: semantics, algorithms, edge cases; tables and repositories added (with the spec sections they extend).
- **Tasks**: numbered; they become `PNN-T1…` in the ledger. Order: ports and tests first, then adapters, then wiring. Each task ends green.
- **Tests**: by layer, with the invariants written as properties where they apply.
- **Exit criteria**: checkable statements ("two workers race on one row; exactly one advances").
- **Decisions to review**: numbered questions, each with a recommended default. **No task that depends on an open decision may start** (`sdlc-workflow` Stage 1). When resolved, strike through and write `**Resolved:** <answer> (<who>, <date>; ADR-NNNN)`.

## Step 4: The outcome doc

Plans are full-scope; outcomes are what we build now. The outcome doc (`outcome-NN-<slug>.md`) is the current build target:
- **Outcome**: one quoted sentence of what a person can do when it is done.
- **What done looks like**: a manual demo script, a table of automated acceptance scenarios (`ID | Scenario | Proves (requirement IDs)`), exit criteria.
- **Scope**: in, and deferred (with the outcome that will pick it up).
- **Build order**: milestones `M1…`, each `Phases | Slice of each phase | You can then…`. Each milestone ends with something that runs.
- **Decisions** made for this outcome, and which open decisions block which milestone.

Agents build only the outcome's slice of each phase, in milestone order. Phase tasks outside the slice go into the ledger as `not started (deferred: <outcome>)`. When the outcome is done, write the next one; the phase docs stay as the design.

## Step 5: Plan for parallel agents

- Draw the dependency graph in the README and a parallelism chart (which phases can run at once).
- Two phases may run in parallel only if their **Modules and files** lists don't overlap and the ports between them are already written. Draft shared contracts (port signatures, request/response models) as an early task of the upstream phase so the downstream one can start.
- Shared hot files (the canonical list is in `workstream-tracking`, "Shared hot files") belong to one task at a time; name the owner in the ledger.
- See `multi-agent-development` for worktrees, claiming, and merging.

## Step 6: After build — "As built"

When a phase (or its outcome slice) is done, append `## As built (<date>, <milestone>, [change record](…), [ADR-NNNN](…))` to the phase doc:
- what was built vs deferred;
- where files differ from the plan;
- **Interfaces later phases rely on**: a `Need | Use` table with exact module paths and signatures.

The plan above it stays as written; "As built" is the truth for later phases. Update the outcome doc's milestone status and the README phase table.

## Gates

| Before | Must be true |
| --- | --- |
| Writing phase docs | Parent plan has requirement IDs, core interfaces, layout, testing strategy |
| Starting a phase | Its ledger exists (`workstream-tracking`); every decision its current tasks depend on is resolved |
| Running phases in parallel | File lists don't overlap; shared ports are written |
| Closing a phase | Exit criteria met with evidence; "As built" written; README and outcome doc updated |
| Closing an outcome | All acceptance scenarios pass as the outcome doc requires; demo works; next outcome drafted or explicitly none |
