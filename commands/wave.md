---
description: Plan and run a wave of parallel worker agents for a phase or a set of tasks - scout the ledger, resolve decisions, claim, then run the kit's wave workflow (workers, anchor, fresh reviewers, fan-in guard) and integrate
argument-hint: <phase or task ids, e.g. P04 or P04-T2 P04-T3>
---
You are the coordinator. This command is the owner's opt-in to multi-agent orchestration for: $ARGUMENTS

1. **Scout inline** (`multi-agent-development`, "The loop", steps 1 to 5): read `HANDOFF.md` and the ledgers; apply "Do you need a wave?"; resolve every open decision these tasks depend on in one message to the owner; split into tasks with disjoint file sets; claim them in the ledger with `Touches`; reserve ADR and migration numbers.
2. **Build the args** for the wave workflow from the ledger, the phase doc, the isolation ADR and `project-guide/knowledge/STACK.md`. The shape is documented at the top of `${CLAUDE_PLUGIN_ROOT}/workflows/wave.js`. Set `max_agents` (default 4; smaller when a usage limit is near) and list the tasks beyond the cap for the next wave. Check the available agent types: if `backend-agent-kit:kit-worker` and `backend-agent-kit:kit-reviewer` are not listed, pass `agent_types` with `general-purpose`.
3. **Run it:** call the Workflow tool with `scriptPath: "${CLAUDE_PLUGIN_ROOT}/workflows/wave.js"` and those args. Show the owner the plan (tasks, cap, isolation, off-limits) before launching. While it runs, do not do a worker's task yourself.
4. **Integrate from the structured result**, not from memory: `verified` tasks per `references/integration-checklist.md` (main patch, shared patch by hand, `deps-lock` if the manifest changed, touched checks); `needs-fixes` and `anchor-red` back to the same worker with the findings and the anchor output; `lost` resumed from their checkpoint patches. Never close the wave on a partial set.
5. **Close:** `check-all` on the integrated branch, ledger rows from `ledger_row`, INDEX rows from `index_row`, the `metrics` object into `HANDOFF.md` "Wave metrics", session log, STATUS, owner update (done, running, needs-you, next).

If the Workflow tool is unavailable, run the same loop with the Agent tool and `references/subagent-prompt-template.md`; you are then the fan-in guard, the anchor (re-run `check` in each workspace yourself) and the reviewer launcher.
