---
name: change-records
description: How every change in this repo is documented — one change record per change in docs/changes/, architecture decision records (ADRs) in docs/decisions/, the change and ADR indexes, commit message format, and code-comment rules (why-comments with requirement IDs, no change-history in code), plus keeping every design doc and published page true to the code. Use whenever you finish or are partway through any code, schema, config, integration, or doc change; whenever a design choice between alternatives is made or reversed; when asked "document this", "log this change", "write an ADR", "what changed and why"; and before committing. Any agent executing any feature or part of development must leave a change record.
---

# Change records

Months from now, someone (often another agent) will need to know what changed, why, how it was verified, and what was left undone. Git shows *what*; change records hold the *why*, the verification evidence, and the follow-ups. ADRs hold the decisions that shape everything after them.

## Change record: one per change

- **Where:** `docs/changes/YYYY/YYYY-MM-DD-<phase-or-area>-<slug>.md`, e.g. `docs/changes/2027/2027-03-02-p04-order-idempotency.md`. Date-plus-slug names let parallel agents create records without colliding.
- **When:** start it at Stage 2 of `sdlc-workflow` (the Design section is the design note); finish it at Stage 7.
- **Template:** `assets/change-record-template.md`. Fill every section; write "None" rather than deleting a section, so readers know it was considered.
- **Index:** append one line to `docs/changes/INDEX.md` (newest first):
  `| 2027-03-02 | P04 | phase-task | [Order idempotency](2027/2027-03-02-p04-order-idempotency.md) | ADR-0007 |`
- **Size:** proportional. A bug fix can be 15 lines; a phase task with a new port can be two pages. Every record still has Verification with the actual commands and results.

What makes a record useful:
- **Why** is in terms of requirements (`OR-12`), invariants, or observed failures, not "improved code".
- **Verification** is evidence (commands and pass counts), not assertions like "tested". Never write a result you didn't see.
- **Deviations** from the phase doc or standards are stated with reasons.
- **Follow-ups** are concrete and also copied into the ledger.

## ADR: one per decision

Write an ADR when a choice will constrain future work: a published interface, a file or wire format, the data model contract, an invariant, a vendor or SDK, a runtime semantic, a process rule, or rejecting a serious alternative.

- **Where:** `docs/decisions/ADR-NNNN-<slug>.md`, numbered sequentially. Reserve the number immediately: create the ADR file with `Status: Proposed` and bump "Next number" in `docs/decisions/INDEX.md` in the same edit, before drafting. If two files still share a number, the later-created one renumbers and fixes its links.
- **Template:** `assets/adr-template.md`. Status: `Proposed` → `Accepted` (or `Rejected`); later `Superseded by ADR-XXXX`. Never edit the decision of an accepted ADR; supersede it.
- **Index:** add a row to `docs/decisions/INDEX.md`.
- Link the ADR from the change record, and update the design doc the decision affects.
- **Amending one clause** of an accepted ADR: the new ADR supersedes only that clause; set the old one's status to `Accepted; clause N superseded by ADR-NNNN`.
- **Owner decisions made in conversation** are recorded as `Accepted` ADRs quoting or paraphrasing the owner, without asking again.

## Commit messages

When the owner asks you to commit, use:

```text
<type>(<scope>): <imperative summary, ≤ 72 chars>

<why, in 1–3 lines, citing requirement IDs or the failure>

Change-Record: docs/changes/2027/2027-03-02-p04-order-idempotency.md
ADR: ADR-0007            (only if applicable)
```

`type`: feat, fix, refactor, test, docs, chore, perf, build. `scope`: phase or module (`p04`, `persistence`, `integrations/<partner>`). End with any attribution lines the session requires. Commit and push only when asked; never force-push a shared branch without explicit approval.

## Comments in code

- Explain **why**, not what. Cite requirement IDs and ADRs where a line exists because of them: `# OR-12 / ADR-0007: re-check the order state before charging`.
- **No change-history comments** ("changed on…", "old logic:", "fixed bug #…"), author tags, or commented-out code. That history belongs in change records and git; in code it rots and misleads.
- `TODO` only with a tracked follow-up: `# TODO(P10-F3): …` where the id exists in a ledger.

## Docs must stay true

Do all of this yourself, without asking the owner (`sdlc-workflow`, "Work autonomously"). A change isn't documented until the docs it made stale are updated in the same change: the phase doc ("As built"), binding specs in `implementation/`, `tech-doc.md`, and the `project-guide` knowledge files (`ARCHITECTURE.md`, `INVARIANTS.md`, `DEBUGGING.md` for new failure patterns, `GLOSSARY.md` for new terms). The change record's "Docs updated" section lists them.

Find every copy of a changed term or value with `grep -rn '<term>' . --include='*.md' --include='*.html' --include='*.yaml'`. Never rewrite history: `docs/changes/*` records, the decisions of accepted ADRs, and archived docs stay as they were.

### Published doc pages (optional)

If the project publishes a doc as a web page (for example the HLD from `docs/site/hld.html`, URL recorded in `project-guide/knowledge/INDEX.md`), then whenever a change alters the source doc:

1. Update the matching sections of the page source so it says what the doc says (keep diagrams simple; update any diagram the change affects).
2. Republish to the same URL with whatever publishing tool the project uses (read the current published version first if the tool requires it).
3. Note "<page> republished" in the change record's "Docs updated".
