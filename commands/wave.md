---
description: Plan and run a wave of parallel worker agents for a phase or a set of tasks, per multi-agent-development
argument-hint: <phase or task ids, e.g. P04 or P04-T2 P04-T3>
---
You are the coordinator. Use the `multi-agent-development` skill ("The loop") for: $ARGUMENTS

Orient from `HANDOFF.md` and the ledgers; resolve every open decision these tasks depend on in one message to the owner; split into tasks with disjoint file sets; claim them in the ledger; launch one `backend-agent-kit:kit-worker` agent per task with a prompt built from `references/subagent-prompt-template.md` (isolation mode and resources per the project's isolation ADR and `STACK.md`); integrate each result with `references/integration-checklist.md`; review with `backend-agent-kit:kit-reviewer` where the change type requires it; audit if three or more docs changed; rewrite `HANDOFF.md` at the end.

Size the wave for usage limits, not only for merges. Never do a worker's task yourself while it runs.
