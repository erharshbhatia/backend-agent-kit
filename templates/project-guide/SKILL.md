---
name: project-guide
description: Orientation for this repository — what the product is, the binding vocabulary and invariants, where every design doc lives and which one wins when they disagree, and how to debug. Use at the start of EVERY task in this repo — before planning, designing, coding, reviewing, debugging, writing docs, or answering questions about how the system, its runtime, database, integrations, phases, or requirements work — even if the task looks small. Also use when someone asks "where is X documented", "what does this term mean", or "what must never break".
---

# Project guide

This repository builds <Project>: <one-sentence description of the product, filled by `project-bootstrap`>. The design lives in `tech-doc.md` (the HLD) and `implementation/` (the build plan, phase docs and binding specs). Progress lives in `docs/workstreams/`, history in `docs/changes/`, decisions in `docs/decisions/`.

Getting oriented takes a few minutes and prevents the most expensive mistakes: using retired vocabulary, breaking an invariant, or building something a design doc already decided differently.

## How to orient

1. Read `knowledge/INDEX.md`: it maps every design doc and says which one is authoritative for what.
2. Read `knowledge/INVARIANTS.md`: the rules no change may break. Skim it before every task; they are short.
3. Read the knowledge file for your task:
   - What we're building and why, requirement IDs → `knowledge/PRODUCT.md`
   - Components, runtime, data, deployables → `knowledge/ARCHITECTURE.md`
   - Something is broken or behaving oddly → `knowledge/DEBUGGING.md`
   - Unsure what a word means, or whether a term is retired → `knowledge/GLOSSARY.md`
   - Which command or tool a skill means by `check`, `deps-sync`, "the composition root" → `knowledge/STACK.md`
4. Read the current outcome doc (`implementation/outcome-NN-<slug>.md`, named in `docs/workstreams/STATUS.md`). Work is outcome-driven: build only the slice of each phase it names, in its milestone order; items it defers are out of scope until a later outcome.
5. Check current progress in `docs/workstreams/STATUS.md` and the ledger for your phase (`workstream-tracking`).
6. Then follow `sdlc-workflow` for the actual work, with `engineering-standards` for any code.

If several agents work at once, also read `multi-agent-development` before claiming anything.

## Authority order when documents disagree

1. An accepted decision record in `docs/decisions/` (newest wins over older ones it supersedes)
2. Binding specs in `implementation/` (for example `database-schema.md`, `repository-pattern.md`, an API or file-format spec)
3. The phase doc `implementation/pNN-*.md` for the phase you are working on
4. `implementation/00-implementation-plan.md` (parent plan)
5. `tech-doc.md` (HLD)

The code is the truth about what *is*; the docs above are the truth about what *should be*. When they differ, that is a bug in one of them: find out which.

If you find a contradiction, don't silently pick one: note it in your change record and fix the lower-authority doc, or raise it with the owner if the fix changes a decision.

## Keeping this guide true

The knowledge files are summaries that point to the source docs. When a change alters architecture, an invariant, a debugging procedure, or vocabulary, update the matching knowledge file in the same change (`change-records` checks this). Stale orientation is worse than none.

| Change | Update |
| --- | --- |
| New component, deployable, table group, or data flow | `ARCHITECTURE.md`, `INDEX.md` if a new doc exists |
| New rule that must never break | `INVARIANTS.md` (needs an ADR) |
| New failure pattern found while debugging | `DEBUGGING.md` "Common signatures" |
| New term, or a term retired | `GLOSSARY.md` |
| A command, tool, or stack file changes | `STACK.md` |
| New goal, requirement prefix, or outcome | `PRODUCT.md` |
