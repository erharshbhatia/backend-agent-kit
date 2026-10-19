---
name: project-bootstrap
description: How to start a new backend project with this kit (installed as the backend-agent-kit plugin, or checked out) — copy the project templates into the repo, pick a stack scaffold, fill every placeholder, write STACK.md, product, glossary and invariants, write the tech doc, derive the implementation plan, outcome and phase docs, create the ledgers, record the first ADRs, and build the P00 foundations phase. Use when the owner says "start a new project", "set up a repo from the kit", "bootstrap", "initialize the project", when /backend-agent-kit:bootstrap runs, or when a repo from this kit still contains `<Project>`-style placeholders.
---

# Project bootstrap

The kit is three things: the **plugin** (generic skills, commands, agents, hooks; installed once, upgraded with `/plugin update`), the **templates** it carries (`templates/`: copied into the project and then owned by the project), and the **scaffolds** (`scaffolds/<stack>/`: a runnable service skeleton per stack that enforces the standards). Bootstrapping turns the generic kit into this project's kit. Do it in order; each step feeds the next.

`<kit>` below is where the kit lives: the plugin root printed at session start ("Plugin root: …"), the `${CLAUDE_PLUGIN_ROOT}` value a command passes you, or a checkout of the repository.

## Order

| # | Step | Produces | Skill |
| --- | --- | --- | --- |
| 1 | Copy the templates, pick a scaffold, fill placeholders | `CLAUDE.md`, `.claude/skills/project-guide/`, `docs/`, `implementation/`, `STACK.md`; no `<…>` tokens left in process files | this one |
| 2 | Write product, glossary, invariants | `project-guide/knowledge/{PRODUCT,GLOSSARY,INVARIANTS}.md` | `project-guide` |
| 3 | Write the tech doc (HLD) | `tech-doc.md` (+ optional `docs/site/hld.html`) | `tech-doc-writing` |
| 4 | Plan the build | `implementation/00-implementation-plan.md`, `outcome-01-<slug>.md`, `pNN-<slug>.md`, `implementation/README.md` | `implementation-planning` |
| 5 | Record the first decisions | ADR-0001… (below) | `change-records` |
| 6 | Create the ledgers | `docs/workstreams/STATUS.md`, `HANDOFF.md`, `OPEN-DECISIONS.md`, `ADHOC.md`, `P00-foundations.md` | `workstream-tracking` |
| 7 | Build P00 foundations | The service skeleton, green `check` | `sdlc-workflow`, `engineering-standards` |
| 8 | Start phase work | Waves of tasks | `multi-agent-development` |

Ask the owner for decisions in **one** batch at step 2–3 (product goals, non-goals, stack and scaffold, external-service test policy, docs in git, commits on task branches or not). Everything else you do without asking.

## 1. Copy the templates, pick a scaffold, fill placeholders

```bash
cd <new-repo> && git init
cp -R <kit>/templates/project-guide .claude/skills/project-guide
cp <kit>/templates/CLAUDE.md CLAUDE.md
cp -R <kit>/templates/docs docs
cp -R <kit>/templates/implementation implementation
```

Pick the scaffold: `ls <kit>/scaffolds/` (today: `python-service`; the contract every scaffold meets is `scaffolds/CONTRACT.md`). Read its `README.md`, `STACK.md` and `BOOTSTRAP.md`. Copy its `STACK.md` to `.claude/skills/project-guide/knowledge/STACK.md`; that file is what every skill means by `check`, `deps-sync`, "the composition root". The scaffold code itself is copied in at P00-T2, with the renames its `BOOTSTRAP.md` lists.

Find every placeholder: `grep -rnE '<(Project|package|PREFIX|domain-words|outcome|retired terms)>' --include='*.md' --include='*.toml' --include='*.yml' --include='*.yaml' --include='*.json' .`

| Placeholder | Meaning | Where it appears |
| --- | --- | --- |
| `<Project>` | Human name of the project | `CLAUDE.md`, `project-guide/SKILL.md`, tech doc and plan templates, the scaffold's descriptions |
| `<package>` | Package name | `CLAUDE.md`, `project-guide/knowledge/*`, plan templates (the scaffold's own name is replaced per its `BOOTSTRAP.md`) |
| `<PREFIX>` | Environment variable prefix (e.g. `ORD`) | `project-guide/knowledge/{INDEX,STACK}.md`, parent-plan template, the scaffold's settings |
| `<domain-words>` | Words generic code must never contain (tenant, customer, workflow names) | `CLAUDE.md`, `project-guide/knowledge/INVARIANTS.md`; also the domain-word guard's config in the scaffold |
| `<retired terms>` | Words the team agreed not to use as system terms | `CLAUDE.md` "Never"; list them in `GLOSSARY.md` "Retired terms" |
| `<outcome>` | An outcome name, used in ledger rows as `not started (deferred: <outcome>)` | filled per row, not at bootstrap |

Vendors (LLM, payments, queues) have no placeholder: add one layer-contract rule per vendor SDK that goes behind a port, and name them in `ARCHITECTURE.md`.

### What is yours and what is the kit's

Everything copied from `templates/` and `scaffolds/` is the project's: edit freely. The plugin's skills (`engineering-standards`, `sdlc-workflow`, `change-records`, `workstream-tracking`, `multi-agent-development`, `implementation-planning`, `tech-doc-writing`, this one) contain nothing project-specific and are never edited per project; project names, prefixes, vendors, domain words, commands and paths go in `project-guide/knowledge/` (especially `STACK.md`), `CLAUDE.md`, the ADRs and the design docs. Upgrading the kit is then `/plugin update backend-agent-kit`, followed by the "Project side" notes of the kit's `CHANGELOG.md` entries since the version recorded in `project-guide/knowledge/INDEX.md`. From a checkout instead of the plugin, diff `<kit>/skills/` against the copy you installed.

## 2. Product, glossary, invariants

- `PRODUCT.md`: what we're building, for whom, goals with numbers, non-goals, requirement-ID prefixes, the current outcome.
- `GLOSSARY.md`: one concept, one name. Include the retired terms and what replaced them.
- `INVARIANTS.md`: keep the kit's generic invariants (layers, repositories, injected time and ids, idempotent boundaries, no secrets, process rules); add the project's product and safety invariants. Each invariant is one sentence a reviewer can check.
- `STACK.md`: true for this project after the scaffold renames (package root, prefix, commands).

## 3–4. Tech doc and plan

Follow `tech-doc-writing`, then `implementation-planning`. The plan must name P00 foundations as the first phase and the first outcome's slice of every phase.

## 5. First ADRs

| ADR | Decision | Notes |
| --- | --- | --- |
| ADR-0001 | Adopt this kit's process (lifecycle, ledger, change records, multi-agent rules) | Accepted at bootstrap; record the kit version |
| ADR-0002 | Stack: the profile (`engineering-standards/references/stacks/<name>.md`) and scaffold, with deviations | Default: the chosen scaffold's stack as its `STACK.md` records it |
| ADR-0003 | Testing policy for external services (LLMs, payment APIs) | Options: real calls in tests tagged `external` (fail, not skip, without a key); recorded fixtures; fakes. State which and why |
| ADR-0004 | Docs in git | Default: `docs/` tracked. If the owner keeps docs local, record it and update `.gitignore` |
| ADR-0005 | Local environment: container stack, ports, dev database rules | Name the dev database agents must never touch, and the host ports (`<PREFIX>_PG_HOST_PORT`, `<PREFIX>_API_HOST_PORT`) when several projects share one machine |
| ADR-0006 | Isolation mode for parallel agents | Worktree mode (the owner allows commits on task branches; "never commit" then applies to the target branch only) or copy mode (no commits: throwaway copies and patches). `git worktree` needs a commit to exist, so a fresh repository is in copy mode until the owner decides. See `multi-agent-development`, "Isolation" |

## 6. Ledgers

Create from `workstream-tracking/assets/` (or keep the copies from `templates/docs/workstreams/`). `STATUS.md` names the current outcome and lists every phase; `HANDOFF.md` names the isolation mode and the off-limits resources from ADR-0005/0006. `P00-foundations.md` gets the checklist below as its task list.

## 7. P00 foundations checklist

| Id | Task | Done when |
| --- | --- | --- |
| P00-T1 | `git init`, ignore file (secrets, caches, dependency dirs, `.claude/worktrees/`), first commit only when the owner asks | the env file is ignored; `git status` clean of secrets |
| P00-T2 | Copy `<kit>/scaffolds/<stack>/` into the repo; do the renames in its `BOOTSTRAP.md` | its proof grep shows only intended hits |
| P00-T3 | `deps-sync`; commit the lock file with the code | the package imports |
| P00-T4 | Settings: database, logging, worker; env example file with no secrets | settings load from the environment and the env file |
| P00-T5 | Domain basics: `Clock`, `IdGenerator`, typed ids, error hierarchy | unit tests green |
| P00-T6 | Persistence: `Database` and `UnitOfWork` ports, database and memory units of work, migration baseline, contract-suite harness | `up`, `migrate`, `migrations-check` green |
| P00-T7 | Composition root; API (`/livez`, `/readyz`), worker loop, CLI | `stack` healthy |
| P00-T8 | Guards: layer contracts, domain words, SQL location, repository completeness, banned APIs | `check` green; a deliberate violation fails each guard |
| P00-T9 | Logging: structured, JSON in containers, trace ids bound per request | one request produces one structured line with ids |
| P00-T10 | Docs: `project-guide/knowledge/INDEX.md` lists every doc; `STACK.md` true; P00 "As built" section; change record | the next agent can run everything from the docs |

Exit: `check` and `check-all` green with output pasted into the P00 change record; an independent review (`backend-agent-kit:kit-reviewer`) found no must-fix issues.

## 8. Start phase work

Resolve the next phases' "Decisions to review" in one batch, then plan waves with `multi-agent-development` (`/backend-agent-kit:wave`).
