# backend-agent-kit

A Claude Code plugin for building backend services with many agents working in parallel. It packages the way we work: from a tech doc, to implementation plans, to phased builds tracked in ledgers, with every change documented and every agent held to the same standards. The process is stack-agnostic; a scaffold per stack makes the standards executable.

## Why this exists

Coding agents are good at writing code and bad at everything around it that makes a codebase survive months of change. Each failure below is something that happened in a real build; each has a fix in this kit.

| What goes wrong with agents | What the kit does about it |
| --- | --- |
| They forget. A new session knows nothing about the last one | External memory in the repo: a resume file (`HANDOFF.md`), per-phase ledgers, one change record per change, ADRs for decisions |
| They drift. Five agents produce five styles and five architectures | One set of standards, enforced by tools (import-linter, guards, ruff banned APIs, mypy strict), not by prose or reviews |
| They claim green. "Tests pass" without running them | Verification is pasted command output. Reporting a result you did not see breaks an invariant |
| They re-decide. The same question gets answered differently each session | Decisions are ADRs. A phase lists "Decisions to review" and cannot start until they are resolved, in one batch, with recommended defaults |
| They collide. Parallel agents edit the same file, share a database, kill each other's processes | One task per agent, in its own copy or worktree, with an explicit list of writable files, a throwaway database and its own ports. Shared hot files belong to one task; the coordinator integrates |
| They build the example, not the system | Business documents are test cases, not the spec. The tech doc designs the general capability and proves it against the inputs |
| They please. Vague requests get silently filled in | Requirements get IDs that tests and code cite. Ambiguity that changes what gets built is a question to the owner, not a guess |

## Principles

The rules the skills encode. Each one is checkable.

1. **Orient before acting.** Every task starts with the index, the invariants and the ledger, even a one-line fix.
2. **Decisions before code.** No task is built while a decision it depends on is open. Settled decisions are reconciled against ADRs without asking; open ones are asked in one batch with defaults.
3. **Docs say what should be, code says what is.** When they disagree, that is a bug in one of them. Authority order: accepted ADR, binding spec, phase doc, parent plan, tech doc. Fix the lower one in the same change.
4. **Every change leaves a record** with the why, the design, the files, and real verification output. Git holds the what.
5. **Standards are enforced by tools.** `make check` runs lint, types, layer contracts, guards and tests with no Docker and no keys. A failing check is fixed in the design, never silenced.
6. **Layers point inward.** Entry points call use cases, use cases call ports, the domain imports nothing with I/O. Vendors live behind adapters; only the composition root picks implementations. Time and ids are injected.
7. **Extend by registering, not branching.** New handlers, integrations and channels are added through registries; no `if kind == ...` chains in core code.
8. **Correct under concurrency and retries.** One writer per aggregate. Every boundary idempotent. External writes record their intent first and reconcile unknown outcomes instead of retrying blindly. Unknown is never coerced to false. Nothing reports success without a confirmed outcome.
9. **The model proposes, deterministic code decides.** A model output never authorizes a write or does arithmetic that matters.
10. **Numbers are derived, assumptions are visible.** Estimates start from an inputs table where every row is a requirement or a stated assumption, so reviewers challenge the input rather than the conclusion.
11. **One task, one agent, one set of files.** Workers never touch shared state except through the coordinator. Waves are sized for what can be lost at once when usage limits kill every agent at the same moment.
12. **Work autonomously, ask narrowly.** Agents do all documentation, verification and ledger work without asking. The owner is asked only for unmade decisions, required approvals and irreversible actions.
13. **Length scales down, presence does not.** A bug fix gets a short record, not no record.
14. **Generic stays generic.** The process skills contain no project names, so a project can pull kit improvements later. Project specifics live in `project-guide/knowledge/` and `CLAUDE.md`.

## Install

```text
/plugin marketplace add erharshbhatia/backend-agent-kit
/plugin install backend-agent-kit@backend-agent-kit
```

Or try it without installing: `claude --plugin-dir /path/to/backend-agent-kit`. The skills also follow the Agent Skills layout (`skills/<name>/SKILL.md`), so `npx skills add erharshbhatia/backend-agent-kit` installs them into other agents; commands, agents and hooks are Claude Code only.

## Start a project

```bash
mkdir my-service && cd my-service && git init
claude
```

Then `/backend-agent-kit:bootstrap my-service python-service`. The `project-bootstrap` skill copies the templates in, picks the scaffold, fills the placeholders, writes `STACK.md`, asks the owner's decisions in one batch, writes the tech doc and the plan, creates the ledgers and the first ADRs, and builds the P00 foundations phase.

## What's inside

| Path | What it is |
| --- | --- |
| `skills/` | The eight process skills (below); loaded by Claude Code when relevant |
| `commands/` | `/backend-agent-kit:bootstrap`, `:status`, `:handoff`, `:audit`, `:wave` |
| `workflows/wave.js` | The wave as code for the Workflow tool: one worker per task with a schema-enforced report, a fresh anchor that re-runs `check`, fresh reviewers (three lenses with majority for heavy changes), a fan-in guard, metrics. Results never pass through the coordinator's context |
| `agents/` | `kit-worker`, `kit-reviewer`, `kit-auditor`, `kit-integrator`: the roles `multi-agent-development` describes |
| `hooks/` | SessionStart: points the session at `HANDOFF.md`. PreToolUse on Bash: blocks `pkill`, force pushes, volume deletes, database drops, hard resets in kit projects (owner escape hatch: `KIT_ALLOW=1`) |
| `templates/` | What bootstrap copies into a project and the project then owns: `CLAUDE.md`, the `project-guide` skill with its knowledge files (`INDEX`, `INVARIANTS`, `STACK`, `ARCHITECTURE`, `PRODUCT`, `GLOSSARY`, `DEBUGGING`), empty ledgers, indexes |
| `scaffolds/` | One runnable service skeleton per stack, all meeting `scaffolds/CONTRACT.md` (`check-contract.sh` verifies it). Today: `python-service` |
| `CHANGELOG.md` | What changed in the kit and what a project has to do to pick it up |

### Skills

| Skill | Use it for |
| --- | --- |
| `project-bootstrap` | Starting a new project: templates, scaffold, placeholders, first docs, first ADRs, P00 |
| `tech-doc-writing` | Writing and evolving the HLD: requirements, estimates, architecture, decisions, open questions |
| `implementation-planning` | Turning the HLD into a parent plan, binding specs, an outcome doc and phase docs |
| `sdlc-workflow` | The lifecycle for every change: orient → intake → design note → plan → build → verify → review → document → close |
| `engineering-standards` | The ten rules (layers, repository + unit of work, registries, typed contracts, errors as values, injected time and ids, tests per layer), the review checklist, and one profile per stack |
| `change-records` | One change record per change, ADRs for decisions, commit format, comment rules, docs stay true |
| `workstream-tracking` | `HANDOFF.md`, `STATUS.md`, per-phase ledgers, open decisions, claiming tasks, the shared-hot-files list |
| `multi-agent-development` | Running parallel agents: the wave-or-not test, worktree or copy isolation, node contracts, waves sized for limits and caps, anchored three-lens review, fan-in guard, layered fan-in, integration |

The project-specific `project-guide` skill is not in the plugin: bootstrap writes it into each project, because its content (invariants, glossary, stack, architecture) belongs to that project.

## Stacks

The skills never name a tool. They say `check`, `deps-sync`, "the composition root", and each project's `project-guide/knowledge/STACK.md` says what that is. A stack is a **profile** (`skills/engineering-standards/references/stacks/<name>.md`: idioms, enforcement mapping) plus a **scaffold** (`scaffolds/<name>/`: runnable skeleton with the same Makefile targets and guards).

| Stack | Profile | Scaffold | Status |
| --- | --- | --- | --- |
| Python 3.12, FastAPI, SQLAlchemy async, Postgres, Alembic | `python-postgres` | `python-service` | reference implementation |
| TypeScript, Node, Postgres | | | wanted; contract in `scaffolds/CONTRACT.md` |
| Go, Postgres | | | wanted |

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
docs/workstreams/HANDOFF.md + STATUS.md + PNN-*.md   resume point, who is doing what, decisions, blockers
        │  sdlc-workflow + engineering-standards (+ multi-agent-development)
        ▼
code + tests + docs/changes/* + docs/decisions/*
```

## Graph, not chain

A wave is a diamond: fan out one worker per independent task, reduce in plain code, verify with fresh agents that never saw the worker's chat, synthesize for the coordinator. The pieces that keep it honest are anchors the agents cannot argue with: the `check` command re-run by a separate agent, invariants changeable only by ADR, pasted command output, and the hook that blocks the dangerous commands. `multi-agent-development` opens with the test for when a wave is the wrong tool.

## Benchmark

There is no benchmark yet, only a baseline. Herald, the first project built with the kit, reached 1,335 unit, 271 database and 22 end-to-end tests in four days, lost six workers at once to a usage limit, and fanned 70 audit findings in by hand. Every wave now writes a metrics row into `HANDOFF.md` (launched, returned, lost, verified, anchor-red, must-fix findings, agents, tokens, `check-all` after integration). Those rows, across projects, are the benchmark. Claims about speed or cost that are not in that table are not claims the kit makes.

## Updating a project from a newer kit

`/plugin update backend-agent-kit`, then read the `CHANGELOG.md` entries since the version recorded in the project's `project-guide/knowledge/INDEX.md` and do their "Project side" items. The plugin's skills carry nothing project-specific, so the update never touches the project's files.

## Working on the kit itself

See `CLAUDE.md` at the root of this repository.
