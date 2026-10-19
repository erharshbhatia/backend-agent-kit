# Integration checklist

Run per worker result, then once per wave.

## Per worker

- [ ] Read the report and the change record. Status is `done` (or partial with clear follow-ups).
- [ ] Diff touches only the files the task listed. Anything else is reverted or explained.
- [ ] Verification output in the change record is real (commands and counts), not "tested".
- [ ] Reviewer subagent run if the change type needs review; must-fix findings resolved.
- [ ] Integrated onto the target: rebase + fast-forward, or `git apply --3way` of the worktree or copy diff (`patch -p1` when the repository has no commits).
- [ ] Copy mode: main patch applied; shared patch read line by line, then applied; `deps-lock` and `deps-sync` rerun if the dependency manifest changed (never a hand-merged lock file).
- [ ] Conflicts resolved. Index and ledger files: both sides' rows kept, newest first.
- [ ] "Needs from coordinator" snippets applied to shared files (composition root, settings, lock file).
- [ ] Touched-area checks green on the target after integration.
- [ ] Ledger row → `done` with change record link. INDEX rows added with small anchored edits.
- [ ] Throwaway databases and servers the worker started are stopped (by PID or container id).

## Per wave

- [ ] Full `check-all` on the integrated branch. Paste pass/fail counts into the owner update.
- [ ] End-to-end or scenario tests the phase names, if any.
- [ ] Consistency audit if three or more docs changed; findings fixed.
- [ ] `STATUS.md` updated; session log entry written with the next step; `HANDOFF.md` rewritten.
- [ ] Worktrees removed only for branches verified merged; unmerged ones listed for the owner.
- [ ] Owner told: done, running, needs-you (one batch), next.

## Red flags (stop and rethink)

- Two workers edited the same function. → Planning error; integrate one, send the other back.
- A worker "fixed" a failing test by changing the assertion. → Reject; ask for the real fix.
- A worker reports green but the change record has no command output. → Re-run checks yourself.
- A worker touched the dev database or killed processes by pattern. → Tell the owner; check for damage.
- A worker reported only at the end, with no checkpoint. → Integrate what exists; restate the checkpoint rule in the next prompt.
