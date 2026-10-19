---
name: sdlc-workflow
description: The mandatory development lifecycle for every piece of work in this repo — orient, intake, design note, plan, build, verify, review, document, close — with explicit gates between stages. Use whenever you are asked to implement, build, start, continue, or finish a phase or a task in one, fix a bug, add or change an integration, endpoint, table, migration, model or prompt, dependency, config or default value, documented parameter, design-doc change, or refactor anything; also when resuming someone else's in-progress work. Use it even for small changes: the stages scale down, they don't disappear.
---

# SDLC workflow

Many agents will build this system over months. The lifecycle below is what lets any of them pick up any piece of work, do it to the same standard, and leave it in a state the next one can trust. Each stage ends with a gate: a concrete condition to meet before moving on. Small changes pass through the same stages quickly; they don't skip them.

First classify the change (it decides which artifacts are required): see `references/change-types.md`.

## Work autonomously

The owner wants the process to run without their involvement. Do every step below yourself, without asking permission or checking in:

- all documentation: change records, ADRs for decisions the owner has already stated, change and ADR indexes, ledger updates, handoff notes;
- keeping every design doc, the `project-guide` knowledge files, and any published doc page true to the code and to each other (see `change-records`, "Docs must stay true");
- verification (`check`, scenario and contract suites; the concrete commands are in `project-guide/knowledge/STACK.md`) and self-review;
- consistency audits and parallel work through subagents (below).

Ask the owner **only** for:
- a product or architecture decision nobody has made yet (including unresolved "Decisions to review");
- the approvals that `references/change-types.md` marks as required;
- outward or irreversible actions: committing or pushing (only when asked), sending anything to external services, deleting others' work, touching shared or production data.

Ask in **one batch**, each question with the doc's recommended default. When you record a decision the owner made in conversation, quote or paraphrase it in the ADR and mark it `Accepted` without asking again.

## Use subagents

- **Parallel work:** independent tasks can run in parallel subagents. Each claims its own task in the ledger first, works only in the files its task owns, and writes its own change record; the coordinating agent merges ledger and index updates at the end. The mechanics (worktrees or throwaway copies, ports, databases, merging) are in `multi-agent-development`.
- **Consistency audit:** after any change that touches three or more docs, or before closing a phase, spawn a read-only reviewer subagent to cross-check the HLD, `implementation/`, `docs/`, and the skills for contradictions, stale references, and broken links; fix what it finds before Stage 8.
- **Independent review:** for change types that need review (Stage 6), a fresh subagent running the review checklist is a valid reviewer.
- Give each subagent the exact files it may write; everything else is read-only for it.
- **Audit recipe** (the only copy; `multi-agent-development` links here): use a general-purpose or planning subagent (not a search-only one, which only locates). Prompt: "Read-only. For terms/sections <list>, cross-check `tech-doc.md`, `docs/site/hld.html` (if the project publishes one), `implementation/*`, `.claude/skills/**`, `docs/decisions/INDEX.md`, `docs/workstreams/*`, and the code under <paths>. Report contradictions, stale values, dead paths and links as file:line → proposed text. Ignore `docs/changes/*`, archived docs, and superseded ADRs." Split large sweeps across several subagents by doc group.

## Stage 0: Orient
- Use the `project-guide` skill; skim `INVARIANTS.md`.
- Read `docs/workstreams/HANDOFF.md` (the resume point), then `STATUS.md` and the ledger for your work (`workstream-tracking`).
- Read the current outcome doc (`implementation/outcome-NN-<slug>.md`). Work toward it: build only the slice of the phase it names, in its milestone order; anything it defers is out of scope unless the owner says otherwise.
- **Gate:** you can name the task ID (or change type), the outcome it serves and its slice, the governing docs, and any task already in progress by another agent.

## Stage 1: Intake
- Read the phase doc (`implementation/pNN-*.md`): goal, scope, files, design details, tasks, tests, exit criteria. Narrow it to the slice the outcome doc names; record deferred tasks in the ledger as `not started (deferred: <outcome>)`.
- Reconcile each **Decision to review** against accepted ADRs (`docs/decisions/INDEX.md`), `docs/workstreams/OPEN-DECISIONS.md`, earlier ledgers, and the phase doc. Mark any already settled as `resolved (ADR-NNNN)` without asking. Put every one still open that your tasks depend on in **one** message to the owner, each with the recommended default. A decision that blocks none of your current tasks does not block starting. Record answers in the ledger, `OPEN-DECISIONS.md`, and an ADR when architectural.
- Restate the task in the ledger: scope in, scope out, requirement IDs, acceptance criteria.
- **Claim** the task in the ledger (status `in progress`, your agent/session id) so nobody else starts it.
- **Gate:** acceptance criteria written; blocking decisions resolved; task claimed.

## Stage 2: Design note
- Required for everything except `docs-only` and trivial fixes (see change types). Write it as the "Design" section of the change record draft (`change-records`, template in its `assets/`).
- Cover: where the code lives (layer/module), ports and signatures, data/schema changes, idempotency and concurrency, failure cases and edges, test plan, doc updates needed.
- Check it against `engineering-standards` and `INVARIANTS.md`.
- If it changes a published interface, a file or wire format, the schema contract, an invariant, a vendor, or rejects an alternative worth remembering → write an ADR (`change-records`).
- **Gate:** design note exists; ADR drafted if needed; owner approval obtained when the change type requires it.

## Stage 3: Plan
- Break the work into small, independently verifiable steps (each ends green). Put them in the ledger's task table.
- Order: ports and tests first, then adapters, then wiring.
- **Gate:** step list in the ledger.

## Stage 4: Build
- Follow `engineering-standards`. Test first for bugs and for clear behaviour.
- Keep each step green (`check` for the touched area) before starting the next.
- Record discoveries (surprises, doc contradictions, follow-ups) in the change record as you go, not at the end.
- **Gate:** all steps done; nothing stubbed without a tracked follow-up.

## Stage 5: Verify
- Run `check` (every gate that needs no Docker and no keys) and, for persistence, schema or runtime changes, `check-all` (adds the database tests and `migrations-check`); concrete commands in `STACK.md`. Then every other suite the change type names: model tests, end-to-end scenarios, contract suites, UI checks. For runtime/data changes also run the crash and duplicate scenarios the phase names. Acceptance scenarios that touch nondeterministic parts (models, timing) must pass several runs in a row (the outcome doc says how many).
- Check every acceptance criterion and the phase exit criteria this task covers.
- Paste the commands and results (pass counts, failures) into the change record's Verification section. If something fails and you can't fix it, say so plainly; **never report green you didn't see**.
- If a named command doesn't exist yet (e.g. `check` before the foundations phase), run the nearest equivalent from the stack profile (the test runner on a path, the linter, the type checker) and state what was unavailable; this doesn't block.
- Never run tests against a shared or developer database you don't own; use a throwaway database (a test container or a per-agent instance).
- **Gate:** all checks green, or failures documented with the owner informed.

## Stage 6: Review
- Self-review with `engineering-standards/references/review-checklist.md`; fix findings.
- For changes of type `feature`, `schema`, `runtime`, `interface`, or `security-sensitive`, also get an independent review (a code-review skill, a fresh read-only subagent given the change record's file list, or a human) and resolve findings.
- **Gate:** checklist clean or deviations justified in the change record; review findings resolved.

## Stage 7: Document
- Finish the change record (`change-records`): summary, why, design, files, schema, tests, verification, docs updated, risks, follow-ups.
- Accept the ADR if one was drafted (status `Accepted`) and update `docs/decisions/INDEX.md`.
- Update every doc the change made stale in the same change: phase doc ("As built"), binding specs, `tech-doc.md`, `project-guide` knowledge files, any published page. Design docs must describe the code as it is.
- **Gate:** change record complete and indexed; no doc contradicts the code.

## Stage 8: Close
- Update the ledger: task status `done` with the change record link, session log entry, blockers, and the next step for whoever continues (`workstream-tracking`).
- Update `docs/workstreams/STATUS.md` if the phase status changed; rewrite `HANDOFF.md` if you are the coordinator or the only session.
- Commit with the message format in `change-records`, only if the owner asked you to commit.
- **Gate:** the next agent could continue from the ledger alone.

## When you must stop and ask

- An unresolved "Decision to review" blocks you.
- The work would break an invariant or change a published interface without an accepted ADR.
- Acceptance criteria are ambiguous in a way that changes what gets built.
- Verification fails and the fix is outside the task's scope.
- A tool or permission denies an action. Don't work around it (no alternate command that achieves the same effect); report it and ask.

## Scaling down

Length scales down, not presence. For `bugfix`, `config`, `dependency`, `refactor` and `docs-only` changes:

- Orient = `INVARIANTS.md`, `HANDOFF.md` and the ledger row you claim; the outcome doc only when the change touches scope.
- Design note = the "What and why" paragraph of the short change record (cause, fix, reproducing test).
- Change record = `change-records/assets/change-record-short-template.md`, about 20 lines.
- Verification is still real output pasted in; a bug still gets its reproducing test before the fix.

So a one-line bug fix gets: a quick orient, a reproduced failing test, the fix, `check`, a short change record, and a ledger line. The full orient and the full template are for `phase-task`, `feature`, `integration`, `schema`, `runtime`, `interface`, `model` and `security-sensitive`.
