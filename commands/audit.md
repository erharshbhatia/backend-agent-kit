---
description: Run the consistency audit - a read-only auditor cross-checks the HLD, implementation docs, skills, ADRs, ledgers and code for contradictions, then fix what it finds
argument-hint: [terms or sections to focus on]
---
Run the audit recipe from the `sdlc-workflow` skill ("Use subagents", audit recipe) with the `backend-agent-kit:kit-auditor` agent. Focus terms or sections: $ARGUMENTS (blank means the areas touched since the last audit, per the ledgers).

Split large sweeps across several auditors by doc group. Fix the findings in the lower-authority document per the authority order in `project-guide`, leave a `docs-only` change record (`change-records`), and report what changed as file:line.
