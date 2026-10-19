---
name: multi-agent-development
description: How a coordinator agent runs several worker agents in parallel on one repository — task splitting into waves, one git worktree and branch per task, claiming and file ownership in the ledger, self-contained subagent prompts, throwaway databases and ports per agent, integrating results (rebase, `git apply --3way`, integration agents), verification before and after merge, independent review and consistency-audit subagents, resuming killed agents, operational safety rules, handoff, and status reporting to the owner. Use whenever work will be split across subagents or parallel sessions, when you are asked to "use subagents", "run in parallel", "fan out", "spin up agents", or "go faster", when merging several agents' branches, when resuming an agent that stopped, and when cleaning up worktrees.
---

# Multi-agent development

One coordinator agent plans, splits, launches, integrates, and reports. Worker agents each build one task in isolation and report back. Done well, five agents finish a phase in the time one agent takes for a task. Done badly, they overwrite each other, corrupt a shared database, and leave a merge nobody can untangle. The rules below are what kept it working.

Use this together with `sdlc-workflow` (every worker still follows the lifecycle), `workstream-tracking` (claims, ledger, handoff), and `change-records` (one record per task).

## Roles

| Role | Does | Never does |
| --- | --- | --- |
| **Coordinator** (the session talking to the owner) | Orients, reads the ledger, splits work into tasks and waves, writes each worker prompt, launches workers, answers their questions from the docs, integrates branches, runs the full suite on the integrated result, merges shared index and ledger rows, reports to the owner | Builds a task it already gave a worker; does an action a worker was denied; edits files a running worker owns |
| **Worker** (subagent, one task) | Claims its task, works only in its own worktree and its own files, follows `sdlc-workflow`, writes its change record, runs its checks, reports once | Spawns more agents; edits files outside its list; touches the dev database or shared services; commits to `main`; pushes |
| **Reviewer** (read-only subagent) | Reviews one diff or change record against the review checklist; reports findings with file:line | Edits anything |
| **Auditor** (read-only subagent) | Cross-checks docs, skills, and code for contradictions and stale values | Edits anything |
| **Integrator** (subagent, optional) | Resolves a heavy merge between branches in its own worktree, runs checks, reports | Changes behaviour beyond resolving the conflict |

## The loop

1. **Orient.** Read `docs/workstreams/STATUS.md`, the phase ledgers, `OPEN-DECISIONS.md`. Know what is in progress and by whom.
2. **Resolve decisions first.** Collect every open decision the planned tasks depend on and ask the owner in **one** message, each with a recommended default. Don't launch workers on unresolved decisions.
3. **Split into tasks.** Each task: one change type, one acceptance list, a known file set. Prefer vertical slices that end green. Size: one worker, a few hours of agent time.
4. **Group into waves.** Tasks in a wave run at the same time and must not share files. Tasks that depend on a port, model, or migration another task creates go in a later wave. See "Waves" below.
5. **Claim.** For each task, add or update its ledger row: status `in progress`, owner (`Claude (subagent, <task>)`), date, and `Touches` (exact paths or globs). Do this before launching, so parallel sessions see it.
6. **Launch.** One worker per task, each in its own worktree (`isolation: "worktree"`), each with a self-contained prompt from `references/subagent-prompt-template.md`. Launch a wave's workers in one message so they run concurrently.
7. **Wait, don't duplicate.** While workers run, don't do their work yourself. Answer the owner's questions, prepare the next wave's prompts, or run audits on finished work. Never guess a running worker's results.
8. **Integrate.** As each worker reports: read its report and change record, review the diff, integrate it onto the target branch (see "Integrating"), run checks, then mark the ledger row.
9. **Review.** For change types that need review, launch a read-only reviewer per task. Fix or send back findings.
10. **Audit.** After a wave that touched three or more docs, run a consistency audit (recipe below). Fix what it finds.
11. **Close.** Full suite on the integrated branch, ledger and STATUS updated, handoff entry written, owner told what's done, what's next, and what needs their decision.

## Waves

- **Wave 0 (often the coordinator alone):** the shared seams. Ports, domain models, settings fields, migrations, the phase doc, ADRs. Everything later waves import.
- **Wave 1..n:** independent tasks over those seams: one adapter, one endpoint group, one UI area, one connector.
- **Last wave:** wiring in the composition root, docs sync, end-to-end tests.
- **Shared hot files** belong to one task per wave: the composition root (`bootstrap.py`), `settings.py`, `pyproject.toml`, the lock file, shared API schema files, migration heads, the UI router. If two tasks need one, either sequence them, or give the file to one task and have the other report "needs in bootstrap: …" for the coordinator to add during integration.
- **Index files** (`docs/changes/INDEX.md`, `docs/decisions/INDEX.md`, `STATUS.md`, `OPEN-DECISIONS.md`, `ADHOC.md`) are edited by the coordinator at integration time, with small anchored edits. Workers put the row they want in their report.
- **ADR numbers:** reserve them before launch (coordinator creates the `Proposed` stubs and bumps "Next number"), then hand each worker its number. Two workers never pick numbers themselves.
- **Migration numbers:** same rule. Hand out revision ids or sequence migrations across waves.
- Keep waves to what you can integrate: 3–6 workers is a good wave. More workers mostly means more merge work.

## Isolation

- **One task = one worktree + one branch.** Launch with `isolation: "worktree"` or create it yourself (`git worktree add .claude/worktrees/<task> -b <task-branch>`). `.claude/worktrees/` is in `.gitignore`.
- **Throwaway resources per agent.** Each worker that needs a database uses a testcontainer or its own throwaway Postgres on its own port. Each worker that runs servers uses its own ports (hand them out: worker 1 → 18110/18111, worker 2 → 18120/18121 …). Write them into the prompt.
- **Never touch the developer database, the shared compose volume, or a server the owner is using.** Name them in every prompt as off-limits.
- **No shared mutable state between workers** except git, and git only through the coordinator.
- Workers do not commit to the target branch. They commit on their own branch (if allowed) or leave the change uncommitted in their worktree; the coordinator integrates.

## Integrating

Pick the lightest method that works:

| Situation | Method |
| --- | --- |
| Branch is behind but doesn't conflict | `git rebase <target>` in the worker's worktree, run checks, fast-forward the target |
| Worker left uncommitted changes | `git -C <worktree> diff --binary > <scratch>/<task>.patch`, then `git apply --3way <scratch>/<task>.patch` on the target |
| Conflicts in prose or index files only | Resolve by hand: keep both sides' rows, newest first |
| Conflicts in code across several files | Launch an integrator subagent in a fresh worktree with both branches named, the intended behaviour of each, and the checks to run |
| Two workers changed the same function | Stop. That was a planning error. Integrate one, then send the other worker back to rebase and redo its part |

After each integration: run the touched area's checks. After the wave: run the full `make check-all` on the integrated branch and paste the result into the owner update. Use `references/integration-checklist.md`.

## Prompts

Every worker starts with no memory of the conversation (unless it is a fork). Its prompt must stand alone:

- the goal in one sentence, and the task id;
- the governing docs to read first (`project-guide`, the phase doc section, ADRs);
- scope in and out;
- the exact files and globs it may write; everything else is read-only;
- resources: its worktree, its ports, its database approach; what is off-limits;
- acceptance criteria;
- verification commands to run and paste;
- what to put in the report (format, max length);
- the safety rules (below) restated briefly.

Template: `references/subagent-prompt-template.md`.

## Review and audit subagents

- **Independent review:** a fresh read-only subagent, given the task's change record and diff (or file list), runs `engineering-standards/references/review-checklist.md` and reports findings as `file:line → issue → proposed fix`, ranked. Fix must-fix items before integration closes.
- **Consistency audit recipe:** use a general-purpose read-only subagent (not a pure search agent). Prompt: "Read-only. For terms/sections <list>, cross-check `tech-doc.md`, `implementation/*`, `.claude/skills/**`, `docs/decisions/INDEX.md`, `docs/workstreams/*`, and the code under <paths>. Report contradictions, stale values, dead paths and links as file:line → proposed text. Ignore `docs/changes/*` and superseded ADRs." Split big sweeps across several auditors by doc group.
- **Code mapping:** to answer "how does X work" across many files, delegate to one read-only agent and keep only its conclusions.

## When agents stop

- **Rate limits or network outages** kill workers mid-task. Their worktree keeps the work. Resume the same agent with `SendMessage` ("continue from where you stopped; re-run your checks"), don't start a new one on the same files.
- **A worker reports it was blocked by a permission denial:** accept it. Don't perform the denied action yourself on its behalf, and don't tell it to find another way around. Surface it to the owner.
- **A worker drifted out of scope:** keep what's in scope, revert the rest in its worktree, record the drift.
- **Two agents claim one task:** the later one stops and releases its claim.

## Safety rules (restate in every worker prompt)

1. Work only in your worktree and your listed files.
2. Never touch the developer database, shared compose volumes, or servers you didn't start. Use your own throwaway database and your own ports.
3. Stop only processes you started, by PID. Never `pkill -f <pattern>` or kill by name: it takes down other agents' servers and the owner's.
4. If a command is denied, stop and report it. Don't work around it (no alternative commands that achieve the same effect, no stash-and-reset tricks).
5. Look before you overwrite or delete: data, files, drafts, branches. If unsure whether it's someone's work, ask.
6. Never print, copy, or commit secrets or `.env`.
7. Don't commit to the target branch, push, or contact external services unless the prompt says so.
8. Report results you actually saw. Paste real command output. Say plainly what failed.

## Cleanup

- Remove a worktree only after verifying its branch is merged (`git branch --merged <target>` or an empty `git diff <target>...<branch>`) and it has no uncommitted changes worth keeping.
- Stop the throwaway databases and servers each worker started (by PID or container id).
- Delete merged branches. Keep unmerged ones and list them for the owner.

## Reporting to the owner

The owner should never have to ask "what's happening". Each update, short:

- **Running:** which workers, on what, since when.
- **Done:** what landed, with check results.
- **Needs you:** decisions, approvals, irreversible actions, in one batch with recommended defaults.
- **Next:** the next wave.

When asked "is it done?", answer from the ledger and the actual check output, not from memory.

## Handoff

At session end, even mid-wave: every ledger row is current (in progress / blocked / done), each in-flight worker's worktree path and state is in the session log, and the exact next step is written. The next coordinator must be able to continue from the ledger alone.

## Optional: UI recording runs

To find usability friction in a UI, launch one agent that builds a realistic piece of work end to end through the UI (Playwright, video on, screenshots at each step) against a throwaway backend. It writes a step log, a friction list ranked by severity, and screenshots. Keep large videos out of git (`docs/recordings/**/video/` in `.gitignore`). Turn the friction list into ledger tasks.
