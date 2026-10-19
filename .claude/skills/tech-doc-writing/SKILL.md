---
name: tech-doc-writing
description: How to write, review, and evolve the project's high-level design (tech-doc.md, the HLD) — turning business inputs into requirement IDs, goals with measurable signals, first-principles workload estimates, architecture, decisions with alternatives, "what breaks first", failure modes, and an open-questions table with owners; plus versioning old tech docs and keeping the HLD (and its optional published HTML page) true to the code. Use whenever starting a new project or system from an idea, BRD, PRD, or flow PDF; when asked to "write the tech doc", "design the system", "do the HLD", "estimate load / cost / storage", "compare alternatives", or "what breaks first"; when a change alters architecture, a decision, a number, or a component the HLD describes; and before writing implementation plans (implementation-planning).
---

# Tech doc writing

The tech doc (`tech-doc.md`) is the HLD every later artifact follows: the parent plan, the phase docs, the specs, the code. Agents and reviewers come back to it for months. It earns that only if its numbers are derived, its decisions name what was rejected, and it still describes the system as built.

## When to write or change it

| Situation | What to do |
| --- | --- |
| New project from an idea, BRD, PRD, or flow documents | Write v1 from `assets/tech-doc-template.md`, then hand off to `implementation-planning` |
| A change alters architecture, a component, a number, or a decision the HLD states | Update the matching sections in the same change (`change-records`, "Docs must stay true") |
| The design changes direction (new runtime, new vocabulary, new core store) | Archive the current file as `tech-doc-vN.md`, write the next version, list it under "Previous versions" |
| Someone asks "why X and not Y?" and the doc doesn't say | Add Y to Alternatives considered |

## How to write it

### 1. Business inputs are test cases, not the spec

BRDs, flow PDFs, handover docs, and example conversations show what the system must handle. They are not the design. Design the general capability, then prove it against the inputs. If the design only works for the inputs you were given, it is a script, not a system.

- List every input document in the header and in the parent plan's input table.
- Distil requirements with IDs grouped by area: `<AREA>-<n>` (e.g. `ORD-3`, `PAY-12`, `X-4` for cross-cutting). Each row cites its source. Tests, graphs, code comments, and reviews reference these IDs.
- Where an input is vague or says "needs discussion", write the assumption you are making and add it to Open questions.

### 2. Lead with decisions

Under the header, keep a **Decisions this version reflects** table (`A1`, `A2`, …): one line per load-bearing choice and the section that explains it. A reader who stops there should know the shape of the system.

### 3. Goals have measurable signals; non-goals are explicit

Each goal (`G1`, `G2`, …) has a signal you could check ("a new flow ships with zero engine deploys", "0 success claims without a confirmed outcome"). Non-goals say what is out of scope and whether a hook is left for it.

### 4. Numbers are derived, assumptions are visible

Do the workload model from first principles (`references/estimates.md`):
- One **Inputs** table: given requirements marked "Requirement", everything else marked "Assumption" with a basis. Reviewers challenge the input, not the conclusion.
- Then derived tables (traffic, storage, database throughput, external APIs, LLM tokens and cost, concurrency via Little's law), each row `Quantity | Calculation | Result`.
- **Conclusions from first principles**: what the numbers rule in and out (e.g. "one Postgres primary is enough; no sharding until ~5–10×").
- **Sensitivity — what breaks first**: `If this changes | First thing to break | Mitigation already in design`.

### 5. Architecture at three zoom levels

Context (who talks to the system), containers (deployables and stores), then one section per major component. Use mermaid or simple diagrams; every arrow labelled. Separate concepts that have different lifetimes (e.g. a short-lived conversation vs a durable process); naming that split early prevents the worst modelling mistakes.

### 6. Every decision names its alternatives

Major choices get a "Decision:" subsection (what, why, what would make us revisit). The **Alternatives considered** table (`Alternative | Why not (now)`) collects every serious option rejected, including the obvious ones (a managed workflow engine, a queue, a distributed database, microservices). "Now" matters: say what would flip the decision.

### 7. Failure, data, infrastructure, observability

- **Failure modes**: `Dependency down | Effect | Degraded behaviour`.
- **Data architecture**: stores and what goes where, schema summary (link the binding spec), consistency across stores, retention and data classification (PII).
- **Infrastructure**: technology mapping, initial sizing at the peak design point, deployment topology, availability targets.
- **Observability**: logs, metrics, traces, and the IDs bound into every event.

### 8. Close with open questions and a review checklist

- **Risks and open questions**: `# | Question | Why it matters | Owner` (Business, Engineering, Security, Legal…). Unanswered questions that block a phase become that phase's "Decisions to review".
- **Design review checklist**: the questions a reviewer will ask ("How is X added without code changes?", "What breaks first?", "How do we avoid double writes?"), each with a one-line answer and the section.

## Style

- Plain words, short sentences, tables over prose. Define each term once; put the binding vocabulary in the glossary (`project-guide` knowledge `GLOSSARY.md`) and use one name per concept everywhere.
- Mark proposals as "proposed" until accepted. Numbers carry units.
- Link to binding specs (`implementation/<spec>.md`) instead of duplicating DDL or formats.

## Keeping it true

- Authority: accepted ADRs > binding specs > phase doc > parent plan > HLD (see `project-guide`). When code or an ADR changes something the HLD states, fix the HLD in the same change; never leave it contradicting the code.
- Find every copy of a changed value: `grep -rn '<term>' . --include='*.md' --include='*.html' --include='*.yaml'`.
- Archived versions (`tech-doc-vN.md`) are history: never edit them, never cite them for decisions.

### Optional published page

If the project publishes the HLD as a web page, its source is `docs/site/hld.html` (styled HTML, diagrams as inline SVG). Record the page URL in `project-guide` `knowledge/INDEX.md`. Whenever `tech-doc.md` changes, update the matching sections of the page, republish to the same URL, and note "HLD page republished" in the change record.

## Gate before planning

Hand off to `implementation-planning` only when:
- every input document is listed and requirements have IDs;
- goals have signals; non-goals are stated;
- the estimates table exists with assumptions marked, and "what breaks first" is filled;
- each load-bearing decision has alternatives;
- open questions have owners.
