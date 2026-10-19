# Implementation docs: <Project> v<N>

This folder breaks the build into small, reviewable phases. Each phase doc covers one module (or a tightly related group) and says what gets built, how, how it is tested, and when it is done.

| Doc | Role |
| --- | --- |
| [`outcome-NN-<slug>.md`](outcome-NN-<slug>.md) | **Current outcome.** What is built now, in which order, and what is deferred |
| [`00-implementation-plan.md`](00-implementation-plan.md) | **Parent.** Scope, requirements, stack, design principles, repo layout, core interfaces, test scenarios, milestones |
| [`database-schema.md`](database-schema.md) | Binding: full schema, access patterns → indexes, concurrency, migrations |
| [`repository-pattern.md`](repository-pattern.md) | Binding: data-access standard (repositories, unit of work, rules) |
| `../tech-doc.md` | The HLD the build follows |

## Current outcome

**Outcome <NN>: <name>** ([`outcome-NN-<slug>.md`](outcome-NN-<slug>.md)). It governs what is built now and in what order (milestones M1–M<n>); the phase docs below stay the design.

## Phases

| # | Phase | Module(s) | Depends on | Est. | Status |
| --- | --- | --- | --- | --- | --- |
| P00 | [Foundations](p00-foundations.md) | repo, tooling, database baseline, bootstrap, settings, logging | — | 1 wk | |
| P01 | [<name>](p01-<slug>.md) | | P00 | | |

## Order and parallelism

```text
week      1    2    3    4    5    6
Agent A   [P00][-P01-][---P02---]
Agent B        [--P03--][P04]
```

- <which phases can start early, and the contract they need first>

## How to review a phase doc

Each doc ends with **Decisions to review**. Agree those before building the phase; everything else in the doc is the default unless someone objects.

## Process

Every agent follows `CLAUDE.md`: orient with `project-guide`, work through `sdlc-workflow`, code to `engineering-standards`, document with `change-records`, track in `workstream-tracking`, and coordinate parallel work with `multi-agent-development`.
