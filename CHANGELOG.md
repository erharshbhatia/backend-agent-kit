# Changelog

Newest first. Each entry says what changed in the kit and what a project bootstrapped earlier has to do to pick it up ("Project side").

## 2026-10-19 — first real-use fixes (from the Herald build)

- **Copy-mode isolation.** `multi-agent-development` now has two isolation modes: git worktrees (needs commits on task branches) and throwaway copies with patches (no commits; what a fresh repository must use, since `git worktree` needs a commit). New ADR-0006 in `project-bootstrap` records the choice. Checkpoint rule for workers; lock files are regenerated, never merged.
- **Waves sized for usage limits**, not only merge load; integrate workers as they report.
- **`docs/workstreams/HANDOFF.md`** is the resume point, read first and rewritten at the end of every coordinator session (template in `workstream-tracking/assets/`).
- **One canonical shared-hot-files list** (`workstream-tracking`, "Shared hot files") and one audit recipe (`sdlc-workflow`); other skills link to them.
- **Generic skills carry no placeholders.** `engineering-standards/**` no longer mentions `<package>`, `<PREFIX>`, `<domain-words>` or `<vendor>`; project names live only in `project-guide/knowledge/` and `CLAUDE.md`. Upgrade recipe in `project-bootstrap`.
- **Short change record** (`change-records/assets/change-record-short-template.md`) for `bugfix`, `config`, `dependency`, `refactor`, `docs-only`; `sdlc-workflow` "Scaling down" names the lighter orient.
- **Scaffold:** `make e2e` and `make test-external` targets; `tests/scenarios/` with S0; `persistence/ports/errors.py` (`ConcurrencyConflict`, `LeaseLost`) and `results.py` (`Created | Existing`, `Page`); host-port variables documented for machines running several projects. Layout statements in `INDEX.md`, the parent-plan template and `lld.md` now agree with the scaffold.

Project side: add `docs/workstreams/HANDOFF.md` from the template; add ADR-0006 (isolation mode); copy the seven generic skills over; add the two Makefile targets, `tests/scenarios/`, and the two ports modules if the project did not already build equivalents; re-point any project edits to `engineering-standards/**` at `project-guide/knowledge/` instead.
