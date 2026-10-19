# Worker prompt template

Copy, fill every `<…>`, delete lines that don't apply. A worker that has to guess will guess wrong.

```text
You are a worker agent building <task id>: <one-sentence goal>.
Execute directly. Do not spawn agents. Report once at the end, then stop.

## Read first
- `.claude/skills/project-guide` (INDEX.md, INVARIANTS.md)
- `sdlc-workflow`, `engineering-standards`, `change-records`
- <implementation/pNN-<slug>.md §<section>>
- <ADR-NNNN, ADR-MMMM>

## Scope
In: <bullets>
Out: <bullets — including things a neighbouring task owns>

## Files you may write (everything else is read-only)
- <path/or/glob/**>
- docs/changes/YYYY/YYYY-MM-DD-<area>-<slug>.md (your change record)
- <ADR-NNNN file reserved for you, if any>
Do NOT edit the shared hot files (`workstream-tracking`, "Shared hot files"), in particular: <the ones this task could be tempted by: the composition root, the settings module, the dependency manifest and lock file, INDEX files, STATUS.md, HANDOFF.md>.
If you need a change there, put the exact snippet in your report under "Needs from coordinator" (copy mode: also as a separate `<task>-shared.patch`).

## Resources
- Isolation: worktree <path> (branch <branch>) — or — copy <path> (baseline commit `baseline`; hand back `git diff --binary` patches). Work only there.
- Checkpoint: after every green step, commit on your branch (worktree) or write `git -C <copy> diff --binary > <scratch>/<task>-checkpoint.patch` (copy). Report the path.
- Database: a test container / your own throwaway database on port <port>. Never the dev database (<host:port>) or compose volumes.
- Ports for any server you start: <port range>.

## Acceptance criteria
1. <observable behaviour>
2. <test that proves it>
3. <doc updated>

## Verify (paste real output in the change record and the report)
- <`check`, or the narrower targets for your area; concrete commands in STACK.md>
- <specific test command / scenario>

## Safety
- Stop only processes you started, by PID. Never pkill by pattern.
- If a command is denied, stop and report it. Do not work around it.
- Look before overwriting or deleting anything. Never print or commit secrets or .env.
- Do not commit to <target branch>, push, or call external services.

## Report
Return the worker report as one JSON object matching `multi-agent-development/references/worker-report-schema.json`
(task_id, status, summary, files_changed, verification with exit codes and counts, change_record, patches {main, shared, checkpoint},
workspace, ledger_row, index_row, needs_from_coordinator, decisions_needed, deviations), then at most 150 words of prose.
The summary field is the only prose inside the object. An anchor agent will re-run `check` in your workspace.
```

## Variants

- **Reviewer:** "Read-only. Review <change record> and the diff `git -C <worktree> diff <target>`. Use `engineering-standards/references/review-checklist.md`. Report findings ranked must-fix / should-fix / nit as `file:line → issue → fix`. Do not edit."
- **Auditor:** see the consistency audit recipe in `SKILL.md`.
- **Integrator:** "In a fresh worktree from <target>, integrate <branch A> and <branch B>. A does <…>, B does <…>; keep both behaviours. Resolve conflicts only; no other changes. Run <checks>. Report the conflicts and how you resolved each."
- **Fork (inherits the conversation):** shorter prompt is fine, but still list writable files, resources, and the report format.
