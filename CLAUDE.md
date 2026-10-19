# <Project> — rules for every agent

<One or two sentences: what this service does, its core idea, and its main stack. Design lives in `tech-doc.md` and `implementation/`.>

## Always

1. **Orient first** with the `project-guide` skill (read `.claude/skills/project-guide/knowledge/INDEX.md` and `INVARIANTS.md`) before planning, coding, reviewing, or answering design questions.
2. **Follow `sdlc-workflow`** for every piece of work (phase task, bug, integration, schema, refactor): orient → intake → design note → plan → build → verify → review → document → close, with its gates.
3. **Write code to `engineering-standards`**: hexagonal layers, repository pattern with unit of work, registries, typed contracts, clean code, tests at the right layer. Run its review checklist before handing over.
4. **Document every change** with `change-records` (change record in `docs/changes/`, ADR in `docs/decisions/` for decisions) and keep every design doc true to the code in the same change.
5. **Keep the ledger** with `workstream-tracking`: claim tasks, record decisions and blockers, and write a handoff entry at the end of every session.
6. **Work autonomously.** Do all documentation, doc syncing, verification, audits, and ledger work without asking. Ask the owner only for unmade decisions, approvals that `sdlc-workflow/references/change-types.md` requires, and outward or irreversible actions.
7. **Run parallel work with `multi-agent-development`**: one task per worktree, claimed in the ledger, exact writable files per agent, throwaway resources per agent, independent review and consistency audits by subagents.

## Never

- Break an invariant in `.claude/skills/project-guide/knowledge/INVARIANTS.md` without an accepted ADR and the owner's agreement.
- Build a task whose governing "Decisions to review" are unresolved; ask the owner in one batch (`sdlc-workflow` Stage 1). Decisions already settled by accepted ADRs are reconciled without asking.
- Put tenant, customer, or workflow-specific concepts (<domain-words>) in the core package `<package>/`.
- Use retired vocabulary as system terms (listed in `GLOSSARY.md`): <retired terms>.
- Report checks as passing without having run them; paste real results into the change record.
- Commit or push unless the owner asks. Never commit secrets or `.env`.
