# Implementation Plan: <Project> v<N>

| | |
| --- | --- |
| Status | Draft for team review |
| Builds on | `../tech-doc.md` (HLD) |
| Business inputs | <documents; the flows they describe> |
| Environment | <e.g. everything runs on one developer machine; external systems are mocked> |
| Goal | <what a working v<N> does, and the property the codebase must keep (new X are additions, not rewrites)> |

---

## 1. Scope of v<N>

### 1.1 In scope

- **<Component>:** <what is built>
- **Mocks:** <local stand-ins for external systems, driven by scenario fixtures, with fault injection>
- **Test harness:** <scenario runner; one scenario per business example>

### 1.2 Out of scope (hooks designed, not built)

| Item | Why deferred | Hook left in v<N> |
| --- | --- | --- |
| | | |

---

## 2. Requirements distilled from the inputs

Each requirement has an ID so tests, code comments, and reviews can reference it.

### 2.1 <Area> (`<AREA>-*`)

| ID | Requirement | Source |
| --- | --- | --- |
| <AREA>-1 | | <document> |

### 2.n Cross-cutting (`X-*`)

| ID | Requirement | Source |
| --- | --- | --- |
| X-1 | | |

---

## 3. What v<N> looks like

<A short narrative or diagram of the running system from a user's point of view.>

## 4. Tech stack

| Concern | Choice | Why |
| --- | --- | --- |
| Stack profile | <name from `engineering-standards/references/stacks/`>, recorded in `project-guide/knowledge/STACK.md` | |
| Language / packaging | | |
| API | | |
| Database, data access, migrations | | |
| Boundary models / validation | | |
| Logging | | |
| Tests | | |
| Quality gates | linter, type checker, layer contracts, guards, behind `check` | |
| <AI / other vendors> | | behind a port |

## 5. Low-level design principles

See `engineering-standards`. Project-specific additions:
- <principle>

## 6. Repository layout

```text
<package root>/
  entrypoints/      api, worker, cli (thin)
  application/      use cases
  domain/           pure models and rules
  persistence/      ports/ (interfaces, errors, results), <database>/, memory/, migrations/
  observability/    logging (and tracing)
  <module>/         one package per outside-facing capability: a port + one adapter per technology
  <composition root>  the only place that picks implementations (file named in STACK.md)
  <settings module>   typed settings from the environment, <PREFIX>_ prefix
mocks/              local stand-ins for external systems
tests/              unit, contracts, application, scenarios
docs/               workstreams/, changes/, decisions/
implementation/     this plan, specs, phase docs, outcome docs
```

## 7. Core interfaces

```text
<module>/port: <Port>
  <intent_named_method>(inputs) -> <TypedResult>
    Guarantees: idempotency, concurrency, what fails and how.
```

Write them in the stack's syntax in the phase docs; here, names and guarantees are what matter.

## 8–N. Component designs

<One section per component the phases build, at plan level: data flow, algorithms in pseudocode, tables touched (link the schema spec).>

## N+1. Testing strategy

| Layer | What | Tools |
| --- | --- | --- |
| Domain | pure logic | unit tests, property tests |
| Application | use cases with memory repositories and fakes | unit tests |
| Contracts | every repository against the database and memory; adapters against mocks | parameterized suites, test containers |
| Scenarios | end-to-end business examples | <scenario runner> |

### Scenarios that must pass for v<N>

| ID | Scenario | Requirements |
| --- | --- | --- |
| S1 | | |

## N+2. Observability (local)

<Logs and IDs bound into every event; what is deferred.>

## N+3. Milestones

| # | Weeks | Deliverables | Exit criteria |
| --- | --- | --- | --- |
| M0 Foundations | 1 | repo, tooling, database baseline, composition root, settings, logging | `check` green on a clean machine |

## N+4. Extension recipes

| To add… | Touch only | Must not touch |
| --- | --- | --- |
| A new <unit of extension> | | core code |
| A new external system | one adapter + its mock | callers |

## N+5. Open items and assumptions

| # | Item | Assumption we build on | Needed from |
| --- | --- | --- | --- |
| 1 | | | |
