---
name: workstream-tracking
description: The progress ledger for this build — docs/workstreams/STATUS.md (current outcome and every phase at a glance), one ledger per phase (tasks, owners, decisions to review and their resolutions, blockers, follow-ups, session log, handoff notes), OPEN-DECISIONS.md and ADHOC.md. Use at the start of any work session to see what's in progress and claim a task, whenever a task changes status or a decision is resolved, when blocked, and at the end of every session to hand off; also when the owner asks "where are we", "what's next", "status of P03", or to resume work another agent started.
---

# Workstream tracking

Work on this system spans months and many agents, often in parallel. The ledger is the shared memory: it says what's done, what's in progress and by whom, what's decided, what's blocking, and exactly where to pick up. If it isn't in the ledger, the next agent doesn't know it.

## Files

| File | Content | Template |
| --- | --- | --- |
| `docs/workstreams/STATUS.md` | Names the current outcome (`implementation/outcome-NN-<slug>.md`) and its milestone; one row per phase: status, owner, % tasks done, blockers, last update, link to ledger | `assets/status-template.md` |
| `docs/workstreams/PNN-<slug>.md` | One ledger per phase: two-digit number and the slug of the phase doc's filename (`p04-orders.md` → `P04-orders.md`). Tasks `P04-T1`, follow-ups `P04-F1`. Created the first time anyone works on that phase | `assets/phase-ledger-template.md` |
| `docs/workstreams/OPEN-DECISIONS.md` | Every "Decision to review" across phases with status and ADR; updated whenever one is resolved | `assets/open-decisions-template.md` |
| `docs/workstreams/ADHOC.md` | Work in done phases or across several phases (bugfixes, small features after release, refactors). A bug in a phase that is in progress or in review goes in that phase's ledger as a task (`P06-T9 bugfix`) | same table shape as a ledger's Tasks + Session log |
| `docs/workstreams/HANDOFF.md` | **Read first in a new session.** Where the build is with verified numbers, every in-flight worker (worktree or copy path, patch state, next step), what needs the owner, the exact next action, current gotchas. Rewritten, not appended, at the end of every coordinator session; the ledgers keep the history | `assets/handoff-template.md` |

Task rows mark whether each task is in the current outcome's slice or deferred (`not started (deferred: <outcome>)`). A phase is done for the outcome when its slice is done, and fully `done` only when every exit criterion is met.

## Protocol

**Start of session**
1. Read `HANDOFF.md`, then `STATUS.md`, then the phase ledger.
2. Check for tasks `in progress` owned by someone else; don't take them unless the owner's last session-log entry says it's released or the owner asks you to.
3. Claim your task: set status `in progress`, owner = your agent/session id, date, and list the files it touches.

**During work**
- Resolved a "Decision to review"? Record the answer, who decided, the date, and the ADR if any, in the Decisions table and `OPEN-DECISIONS.md`.
- Blocked? Add a Blockers row (what, since when, who can unblock) and set the task to `blocked`.
- Found follow-up work? Add it to Follow-ups with an id (`P03-F2`) so a code `TODO` can reference it.

**End of session** (always, even if unfinished)
- Update the task row (status, change record link).
- Add a Session log entry: date, agent, what was done, what's verified (with real results), exact next step.
- Update `STATUS.md` if the phase status, owner, or blockers changed.
- Rewrite `HANDOFF.md` if you are the coordinator or the only session: a worker reports to its coordinator instead.

## Concurrent sessions

Several agents or sessions may share one repository (see `multi-agent-development` for worktrees and merging).
- Re-read a shared file immediately before editing it; use small anchored edits, never whole-file rewrites, on `STATUS.md`, `OPEN-DECISIONS.md`, both INDEX files, and `ADHOC.md`. Edit only your own `STATUS.md` row.
- List the files each task touches in its task row (`Touches`). Never edit a file another in-progress task lists; add a Blocker instead.
- Shared hot files (below) belong to one task at a time.
- Cross-phase dependencies become cross-ledger Blockers (e.g. P05 waits on the P04 task that defines a port).

## Shared hot files

The canonical list; other skills link here instead of copying it. Each of these belongs to one task per wave. Anyone else who needs a change there reports the exact snippet ("needs in the composition root: …") and the coordinator applies it at integration.

| Group | Files |
| --- | --- |
| Composition and config | the composition root, the settings module, the env example file |
| Dependencies | the dependency manifest and the lock file (never hand-merged; rerun `deps-lock`) |
| Tooling | the task runner file (`Makefile`), the layer-contract config, the guards config, the container files, the migration tool config |
| Shared code | shared contract or payload models, the entrypoint routers and CLI command table, the migration chain head, a registry's central module |
| Process docs | `docs/changes/INDEX.md`, `docs/decisions/INDEX.md`, `STATUS.md`, `OPEN-DECISIONS.md`, `ADHOC.md`, `HANDOFF.md`, `implementation/README.md`, `project-guide/knowledge/INDEX.md` |

`project-guide/knowledge/STACK.md` names the concrete files for the project's stack. Projects add rows (a UI router, a shared schema file) here. Re-read any of these immediately before editing; small anchored edits only.

## Status values

`not started` · `ready` (decisions resolved) · `in progress` · `blocked` · `in review` · `done` · `dropped` (with reason)

A phase is `ready` only when all its "Decisions to review" are resolved, and `done` only when every exit criterion in its phase doc is met, with change records linked.

## Style

Short and factual; link rather than copy (change records hold the details). Keep the most recent session log entry at the top. Never delete history; mark items `dropped` with a reason instead.
