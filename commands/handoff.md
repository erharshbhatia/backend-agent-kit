---
description: End the session properly - update ledger rows and session logs, STATUS.md, and rewrite HANDOFF.md so the next session can continue alone
argument-hint: [notes for the next session]
---
Use the `workstream-tracking` skill ("End of session") and, if workers are or were running, the `multi-agent-development` skill ("Handoff").

Update every task row you touched, write the session log entries with real verified results, update `STATUS.md` if a phase changed, then rewrite `docs/workstreams/HANDOFF.md` from its template: where we are, in flight, needs the owner, next action, gotchas. Extra notes from the owner: $ARGUMENTS

Finish by printing the "Next action" section.
