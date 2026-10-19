# Changelog

Newest first. Each entry says what changed in the kit and what a project bootstrapped earlier has to do to pick it up ("Project side").

## 2026-10-19 — 0.3.0: graph engineering

The kit reviewed against graph-engineering principles (node contracts, real edges only, fresh verifiers, anchors, fan-in guards, caps). It was strong on anchors, isolation and human gates, weak on topology. This release fixes the topology.

- **Wave as code.** `workflows/wave.js` for the Workflow tool, run by `/backend-agent-kit:wave`: one `kit-worker` per task capped by `max_agents`, a schema-enforced worker report, a fresh anchor agent that re-runs `check` in each workspace, fresh `kit-reviewer`s per task (three lenses and majority for heavy change types), a fan-in guard that counts returned against launched, verdicts and ledger rows computed in plain code, a metrics object. Results stay inside the script. Integration stays with the coordinator.
- **Node contract.** `multi-agent-development/references/worker-report-schema.json`: the worker's output shape. The prompt template and `kit-worker` return it; prose is one field.
- **Anchored review.** `kit-reviewer` re-runs `check` before judging the diff; a green it cannot reproduce is a must-fix. Three lenses mapped onto the review checklist sections. `sdlc-workflow` Stage 6 uses the same rule.
- **"Do you need a wave?"** opens `multi-agent-development`: fewer than three independent tasks, exploration, step-by-step approval, or a real chain means one agent, not a wave.
- **Real edges only at task close.** Stages 6 and 7 and the audit run in parallel; bootstrap steps 5 and 6 too.
- **Fan-in guard and layered fan-in.** A wave never closes on a partial set; more than four reports or twenty findings are batched through subagents.
- **Caps and metrics.** `max_agents` and an optional budget per wave; a "Wave metrics" table in `HANDOFF.md` and a line in the ledger session log. This table is the kit's benchmark.

Project side: add the "Wave metrics" section to `HANDOFF.md`; workers now return the JSON report (update any local prompt copies); reviews of heavy change types use three reviewers; use `/backend-agent-kit:wave` for waves.

## 2026-10-19 — 0.2.0: plugin layout, stack profiles, hooks and agents

- **Plugin layout.** Skills moved to `skills/`, manifests in `.claude-plugin/` (plus a Codex manifest). Install with `/plugin marketplace add erharshbhatia/backend-agent-kit` and `/plugin install backend-agent-kit@backend-agent-kit`. Generic skills are now upgraded with `/plugin update`; nothing project-specific lives in them.
- **Templates and scaffolds split out.** `templates/` holds what a project owns after bootstrap (`CLAUDE.md`, the `project-guide` skill and knowledge files, ledgers, indexes). `scaffolds/<stack>/` holds the service skeletons; `scaffolds/CONTRACT.md` says what every scaffold provides and `scaffolds/check-contract.sh` verifies it.
- **Stack-agnostic process.** The skills no longer name Python, Postgres, uv, pytest, Alembic or make targets. They use abstract names (`check`, `check-all`, `test-db`, `migrations-check`, `deps-sync`, `deps-lock`, "the composition root", "the atomic claim primitive") that each project's new `project-guide/knowledge/STACK.md` maps to real commands, tools and files. `engineering-standards` keeps the ten rules and R1–R15 generic and gained `references/stacks/README.md` (profile contract) and `references/stacks/python-postgres.md` (everything Python and Postgres, moved there).
- **Commands.** `/backend-agent-kit:bootstrap`, `:status`, `:handoff`, `:audit`, `:wave`.
- **Agents.** `kit-worker`, `kit-reviewer`, `kit-auditor`, `kit-integrator`, matching the roles in `multi-agent-development`.
- **Hooks.** SessionStart prints the plugin root and the head of `HANDOFF.md` in kit projects. PreToolUse on Bash blocks `pkill`/`killall`, force pushes, compose volume deletes, `dropdb`/`DROP DATABASE`, `git reset --hard` and `git clean -f` in kit projects; `KIT_ALLOW=1` is the owner's escape hatch.
- **Scaffold.** `python-service` gained `STACK.md`, `BOOTSTRAP.md` (the renames, moved out of `project-bootstrap`) and a `lock` target.

Project side: copy `scaffolds/python-service/STACK.md` to `.claude/skills/project-guide/knowledge/STACK.md` and fill it for the project; install the plugin and delete the project's copies of the seven generic skills (keep `project-guide`); update `CLAUDE.md` rule wording if it names `make check` (the template now says `check`); re-read `INVARIANTS.md` #1, #2, #4, #10 (store-neutral wording) and keep or adopt it.

## 2026-10-19 — first real-use fixes (from the Herald build)

- **Copy-mode isolation.** `multi-agent-development` now has two isolation modes: git worktrees (needs commits on task branches) and throwaway copies with patches (no commits; what a fresh repository must use, since `git worktree` needs a commit). New ADR-0006 in `project-bootstrap` records the choice. Checkpoint rule for workers; lock files are regenerated, never merged.
- **Waves sized for usage limits**, not only merge load; integrate workers as they report.
- **`docs/workstreams/HANDOFF.md`** is the resume point, read first and rewritten at the end of every coordinator session (template in `workstream-tracking/assets/`).
- **One canonical shared-hot-files list** (`workstream-tracking`, "Shared hot files") and one audit recipe (`sdlc-workflow`); other skills link to them.
- **Generic skills carry no placeholders.** `engineering-standards/**` no longer mentions `<package>`, `<PREFIX>`, `<domain-words>` or `<vendor>`; project names live only in `project-guide/knowledge/` and `CLAUDE.md`. Upgrade recipe in `project-bootstrap`.
- **Short change record** (`change-records/assets/change-record-short-template.md`) for `bugfix`, `config`, `dependency`, `refactor`, `docs-only`; `sdlc-workflow` "Scaling down" names the lighter orient.
- **Scaffold:** `make e2e` and `make test-external` targets; `tests/scenarios/` with S0; `persistence/ports/errors.py` (`ConcurrencyConflict`, `LeaseLost`) and `results.py` (`Created | Existing`, `Page`); host-port variables documented for machines running several projects. Layout statements in `INDEX.md`, the parent-plan template and `lld.md` now agree with the scaffold.

Project side: add `docs/workstreams/HANDOFF.md` from the template; add ADR-0006 (isolation mode); copy the seven generic skills over; add the two Makefile targets, `tests/scenarios/`, and the two ports modules if the project did not already build equivalents; re-point any project edits to `engineering-standards/**` at `project-guide/knowledge/` instead.
