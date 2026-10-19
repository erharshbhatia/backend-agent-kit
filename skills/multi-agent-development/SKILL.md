---
name: multi-agent-development
description: How a coordinator agent runs several worker agents in parallel on one repository — task splitting into waves, one git worktree and branch per task, claiming and file ownership in the ledger, self-contained subagent prompts, throwaway databases and ports per agent, integrating results (rebase, `git apply --3way`, integration agents), verification before and after merge, independent review and consistency-audit subagents, resuming killed agents, operational safety rules, handoff, and status reporting to the owner. Use whenever work will be split across subagents or parallel sessions, when you are asked to "use subagents", "run in parallel", "fan out", "spin up agents", or "go faster", when merging several agents' branches, when resuming an agent that stopped, and when cleaning up worktrees.
---

# Multi-agent development

One coordinator agent plans, splits, launches, integrates, and reports. Worker agents each build one task in isolation and report back. Done well, five agents finish a phase in the time one agent takes for a task. Done badly, they overwrite each other, corrupt a shared database, and leave a merge nobody can untangle. The rules below are what kept it working.

Use this together with `sdlc-workflow` (every worker still follows the lifecycle), `workstream-tracking` (claims, ledger, handoff), and `change-records` (one record per task).

## Do you need a wave?

A wave buys width, not judgment. Run the edge test on the candidate tasks: does task B need anything task A produces (a port, a model, a migration, a file)? If yes, that is a real edge and they are sequential. Count the tasks left with no edge between them and no shared files.

| Situation | Do this instead |
| --- | --- |
| Fewer than three independent tasks | One agent, one task after another. The coordination costs more than it saves |
| The owner wants to approve each step | One agent they can steer; a wave's point is running without them |
| Nobody knows yet what the work is (exploration, a bug whose cause is unknown) | One agent, a loop: try, check, adjust |
| Every task depends on the previous one | A loop; the chain is real |

Three or more independent tasks with disjoint files, decisions resolved, and a coordinator who will not touch them while they run: that is a wave.

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
3. **Split into tasks.** A task is a node: one bounded job, a defined input (the prompt), a defined output (the worker report, `references/worker-report-schema.json`). Each task: one change type, one acceptance list, a known file set. Prefer vertical slices that end green. Size: one worker, at most a couple of hours of agent time; a task that needs a day is two nodes with an edge, not one.
4. **Group into waves.** Tasks in a wave run at the same time and must not share files. Tasks that depend on a port, model, or migration another task creates go in a later wave. Set the wave's caps before launching: `max_agents` (default 4) and, when the owner gave one, a token or cost budget; write both in the ledger session log. See "Waves" below.
5. **Claim.** For each task, add or update its ledger row: status `in progress`, owner (`Claude (subagent, <task>)`), date, and `Touches` (exact paths or globs). Do this before launching, so parallel sessions see it.
6. **Launch.** Preferred: `/backend-agent-kit:wave`, which runs `workflows/wave.js`: one worker per task in its own copy or worktree, a fresh anchor agent that re-runs `check` in each workspace, fresh reviewers per task, and a fan-in guard, all coordinated in code so results never pass through your context. Fallback without the Workflow tool: one worker per task with a self-contained prompt from `references/subagent-prompt-template.md`, launched in one message; you are then the anchor, the fan-in guard and the reviewer launcher.
7. **Wait, don't duplicate.** While workers run, don't do their work yourself. Answer the owner's questions, prepare the next wave's prompts, or run audits on finished work. Never guess a running worker's results.
8. **Integrate.** As each task comes back `verified`: read its report and change record, integrate it onto the target branch (see "Integrating"), run the touched checks yourself, then mark the ledger row. Count: returned versus launched. A wave is never closed on a partial set; every missing task is listed in `HANDOFF.md` "In flight" with its checkpoint path.
9. **Review.** Every task gets a fresh reviewer that first re-runs `check` in the workspace (the anchor) and then judges the diff. Heavy change types (`feature`, `schema`, `runtime`, `interface`, `security-sensitive`) get three reviewers with different lenses (correctness, invariants, tests; the lens map is at the top of the review checklist) and a majority decides. Must-fix findings go back to the same worker; you do not fix them yourself.
10. **Audit.** After a wave that touched three or more docs, run a consistency audit (recipe below). Fix what it finds.
11. **Close.** Full suite on the integrated branch, ledger and STATUS updated, handoff entry written, owner told what's done, what's next, and what needs their decision.

## Waves

- **Wave 0 (often the coordinator alone):** the shared seams. Ports, domain models, settings fields, migrations, the phase doc, ADRs. Everything later waves import.
- **Wave 1..n:** independent tasks over those seams: one adapter, one endpoint group, one UI area, one connector.
- **Last wave:** wiring in the composition root, docs sync, end-to-end tests.
- **Shared hot files** belong to one task per wave. The canonical list is in `workstream-tracking`, "Shared hot files"; don't copy it here. If two tasks need one, either sequence them, or give the file to one task and have the other report "needs in the composition root: …" for the coordinator to add during integration.
- **Index files** (`docs/changes/INDEX.md`, `docs/decisions/INDEX.md`, `STATUS.md`, `OPEN-DECISIONS.md`, `ADHOC.md`) are edited by the coordinator at integration time, with small anchored edits. Workers put the row they want in their report.
- **ADR numbers:** reserve them before launch (coordinator creates the `Proposed` stubs and bumps "Next number"), then hand each worker its number. Two workers never pick numbers themselves.
- **Migration numbers:** same rule. Hand out revision ids or sequence migrations across waves.
- **Size waves for limits, not only for merges.** 3–6 workers is a good wave when nothing else constrains it. Usage, session and rate limits kill every running worker at the same moment, so a wave is also the amount of work you can afford to lose at once: keep it to 3–4 when a limit is near, make workers checkpoint (see "Isolation"), and integrate finished workers as they report instead of waiting for the whole wave.

## Isolation

Two modes. The project's isolation ADR (`project-bootstrap`, ADR-0006) says which applies; until it exists, a repository with no commits is in copy mode.

| Mode | When | How |
| --- | --- | --- |
| **Worktree** | The repository has commits and the owner allows commits on task branches | One task = one worktree + one branch: launch with `isolation: "worktree"` or `git worktree add .claude/worktrees/<task> -b <task-branch>` (`.claude/worktrees/` is git-ignored). Workers commit on their branch, never on the target; the coordinator integrates |
| **Copy** | The repository has no commits yet, or the owner forbids commits (the kit's default `CLAUDE.md` rule) | One task = one throwaway copy: `rsync -a --exclude .git --exclude <dependency dir, e.g. .venv or node_modules> <repo>/ <scratch>/<task>/`, then inside the copy `git init -q && git add -A && git commit -qm baseline` so the worker has a diff base, then `deps-sync` there (STACK.md). The worker hands back patches (`git -C <copy> diff --binary > <scratch>/<task>.patch`); the coordinator applies them to the repository with `git apply --3way`, or `patch -p1` when the repository has no commits |

`git worktree` needs at least one commit, so a fresh project cannot use it; copy mode costs a `deps-sync` and some disk per copy, worktree mode costs a decision about commits. In both modes:

- **Throwaway resources per agent.** Each worker that needs a database uses a test container or its own throwaway database on its own port. Each worker that runs servers uses its own ports (hand them out: worker 1 → 18110/18111, worker 2 → 18120/18121 …). Write them into the prompt. Several projects on one machine each need their own compose host ports too (`PG_HOST_PORT` and `API_HOST_PORT` under the project's env prefix; the local-environment ADR names them).
- **Never touch the developer database, the shared compose volume, or a server the owner is using.** Name them in every prompt as off-limits.
- **No shared mutable state between workers** except git, and git only through the coordinator.
- **Checkpoint early.** Workers commit on their branch (worktree) or write a patch (copy) after every green step, not only at the end, and report the path. A worker killed mid-task then leaves work the coordinator can resume (see "When agents stop").
- Workers never commit to the target branch; the coordinator integrates.

## Integrating

Pick the lightest method that works:

| Situation | Method |
| --- | --- |
| Branch is behind but doesn't conflict | `git rebase <target>` in the worker's worktree, run checks, fast-forward the target |
| Worker left uncommitted changes | `git -C <worktree> diff --binary > <scratch>/<task>.patch`, then `git apply --3way <scratch>/<task>.patch` on the target |
| Worker in copy mode | Same patch flow from the copy's baseline commit. Ask for two patches when shared hot files were touched: `<task>-main.patch` (its own files) and `<task>-shared.patch` (shared files), so the shared one is reviewed line by line and applied by hand. A repository with no commits takes `patch -p1 < <patch>` |
| Lock file changed | Never merge it by hand. Apply the code and dependency-manifest changes, run `deps-lock` then `deps-sync` on the target, and check the lock diff is only the expected packages |
| Conflicts in prose or index files only | Resolve by hand: keep both sides' rows, newest first |
| Conflicts in code across several files | Launch an integrator subagent in a fresh worktree with both branches named, the intended behaviour of each, and the checks to run |
| Two workers changed the same function | Stop. That was a planning error. Integrate one, then send the other worker back to rebase and redo its part |

After each integration: run the touched area's checks. After the wave: run the full `check-all` on the integrated branch and paste the result into the owner update. Use `references/integration-checklist.md`.

## Prompts

Every worker starts with no memory of the conversation (unless it is a fork). Its prompt must stand alone:

- the goal in one sentence, and the task id;
- the governing docs to read first (`project-guide`, the phase doc section, ADRs);
- scope in and out;
- the exact files and globs it may write; everything else is read-only;
- resources: its worktree or copy, its ports, its database approach; what is off-limits;
- the isolation mode, how to hand work back (branch or patch), and the checkpoint rule;
- acceptance criteria;
- verification commands to run and paste;
- what to put in the report (format, max length);
- the safety rules (below) restated briefly.

Template: `references/subagent-prompt-template.md`.

## Review and audit subagents

- **Independent review:** a fresh read-only subagent (`backend-agent-kit:kit-reviewer`), given the workspace, the change record and the acceptance criteria, never the worker's chat. It re-runs `check` first, then judges the diff through its lens and reports `where → issue → fix`, ranked, with an integrate-as-is verdict. Three lenses and a majority for heavy change types. Must-fix items go back to the worker before integration closes.
- **Layered fan-in:** more than four reports, or more than twenty findings, never land in your context raw. Batch them (by task or by doc group), give each batch to one subagent that applies or summarizes it, and read the summaries only. Herald's two audits returned 70 findings; the batch that was not delegated cost a session.
- **Consistency audit:** the recipe (prompt, scope, what to ignore) is in `sdlc-workflow`, "Use subagents"; run it as written there after any wave that touched three or more docs, split across several auditors by doc group.
- **Code mapping:** to answer "how does X work" across many files, delegate to one read-only agent and keep only its conclusions.

## When agents stop

- **Rate limits, usage limits or network outages** kill workers mid-task, usually all of them at once. Their worktree or copy keeps the work, plus any checkpoint patch. Look at what is there first (`git -C <copy> diff --stat`, the checkpoint patches), then resume the same agent with `SendMessage` ("continue from where you stopped; re-run your checks"), don't start a new one on the same files.
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
- **Wave metrics:** launched, returned, lost, verified, needs-fixes, anchor-red (worker claimed green, anchor said red), must-fix findings, agents used, tokens. The same row goes into `HANDOFF.md`; it is the kit's benchmark.
- **Needs you:** decisions, approvals, irreversible actions, in one batch with recommended defaults.
- **Next:** the next wave.

When asked "is it done?", answer from the ledger and the actual check output, not from memory.

## Handoff

At session end, even mid-wave: rewrite `docs/workstreams/HANDOFF.md` (`workstream-tracking`, template in its `assets/`) with where the build is and its verified numbers, each in-flight worker's worktree or copy path and patch state, what needs the owner, and the exact next action; keep every ledger row current (in progress / blocked / done). The next coordinator must be able to continue from `HANDOFF.md` and the ledgers alone.

## Optional: UI recording runs

To find usability friction in a UI, launch one agent that builds a realistic piece of work end to end through the UI (Playwright, video on, screenshots at each step) against a throwaway backend. It writes a step log, a friction list ranked by severity, and screenshots. Keep large videos out of git (`docs/recordings/**/video/` in `.gitignore`). Turn the friction list into ledger tasks.
