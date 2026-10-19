# HLD: <Project> — <one-line description of the system>

| | |
| --- | --- |
| Status | Draft for design review (v1) |
| Scope | <components this doc covers> |
| Out of scope | <what this doc deliberately does not design; hooks only> |
| Business inputs | <list every BRD / flow / handover doc>. Used as **test cases**, not as the specification |
| Build plan | [`implementation/`](implementation/README.md): parent plan, phase plans, binding specs |
| Previous versions | `tech-doc-vN.md` (<what changed>) — or "None" |

**Decisions this version reflects:**

| # | Decision | Where |
| --- | --- | --- |
| A1 | <load-bearing choice in one sentence> | §<n> |
| A2 | | |

---

## 1. Problem

<Two or three paragraphs: who has the problem, what outcome they need, what makes it hard. Name the property that must hold as the system grows (e.g. "new flows ship without code changes").>

### 1.1 Goals

| # | Goal | Measurable signal |
| --- | --- | --- |
| G1 | | |

### 1.2 Non-goals

| Non-goal | Hook left (if any) |
| --- | --- |
| | |

## 2. Design principles

<Five to eight numbered principles that settle future arguments, e.g. "Determinism for effects, models for understanding", "One store until the numbers say otherwise". Each with one sentence of why.>

## 3. Core concepts

| Concept | What it is | Lifetime | Stored in |
| --- | --- | --- | --- |
| | | | |

<State the single most important modelling decision and why (often: which concepts are kept separate).>

## 4. Workload model and back-of-the-envelope estimates

See the `tech-doc-writing` skill's `references/estimates.md` for the method.

### 4.1 Inputs

Only rows marked "Requirement" are given. Everything else is an assumption so reviewers can challenge the number rather than the conclusion.

| Parameter | Value | Basis |
| --- | --- | --- |
| Peak requests | <n>/s | Requirement |
| Average-to-peak ratio | <r> | Assumption: <why> |
| Burst above peak | <k>× for ≤ <t> min | Assumption |
| External calls per request | <n> | Assumption |
| LLM calls per request (if any) | <n> | Assumption |
| Tokens per LLM call | <in> / <out> | Assumption |
| Payload / row sizes | <bytes> | Assumption |

### 4.2 Traffic

| Quantity | Calculation | Result |
| --- | --- | --- |
| Daily requests | avg/s × 86,400 | |
| Peak in-flight requests | peak/s × latency (Little's law) | → design for <n> |

### 4.3 External integrations

| Quantity | Calculation | Result |
| --- | --- | --- |
| Peak external calls | | |
| After cache | | |
| In-flight external calls | | |

### 4.4 LLM (if used)

| Quantity | Calculation | Result |
| --- | --- | --- |
| Peak requests | | |
| Peak input / output tokens per minute | | |
| Daily cost at placeholder rates | | |

<Cost shape paragraph and levers, in order of impact.>

### 4.5 Storage

| Data | Size per item | Daily volume | Retention | Total |
| --- | --- | --- | --- | --- |
| | | | | |

### 4.6 Database and compute throughput

| Quantity | Calculation | Result |
| --- | --- | --- |
| Writes at peak | | |
| Reads at peak | | |
| WAL / log volume | | |
| Compute at peak | | |

**Conclusions from first principles:**
- <what the numbers rule in or out>
- <the binding constraints, in order>

### 4.7 Sensitivity — what breaks first

| If this changes | First thing to break | Mitigation already in design |
| --- | --- | --- |
| | | |

## 5. Architecture overview

### 5.1 Context

```mermaid
flowchart LR
    USERS["<actors>"] --> SYS["<Project>"]
    SYS --> EXT["<external systems>"]
```

### 5.2 Containers

<Deployables and stores, with labelled arrows.>

### 5.3 Deployables

| Deployable | Role | Scales by | State |
| --- | --- | --- | --- |
| api | | | stateless |
| worker | | | stateless |
| database | | vertically | all durable state |

## 6. Request processing — the main path

<Step-by-step for the hottest path: ingress, validation, the core use case, persistence, response. Include a latency budget if latency matters.>

## 7–N. Component sections

<One section per major component. Each: responsibility, interface (port) it exposes, how it is extended, key semantics (idempotency, ordering, concurrency), and a "Decision:" subsection for each load-bearing choice.>

## N+1. Data architecture

### Stores and what goes where
### Schema (summary; binding spec: `implementation/database-schema.md`)
### Consistency across stores
### Retention and data classification

## N+2. Infrastructure

### Technology mapping
### Initial sizing (peak design point)
### Deployment topology
### Availability targets (proposed)

## N+3. Failure modes

| Dependency / fault | Effect | Degraded behaviour |
| --- | --- | --- |
| Database down | | |
| External API slow / down | | |
| LLM provider down (if used) | | |
| Process crash mid-request | | |

## N+4. Security and privacy

<Authentication, authorization, secrets, PII handling, webhook signatures. Mark what is out of scope and the hook left.>

## N+5. Observability

<Logs (structured, IDs bound), metrics (golden signals + domain backlog), traces, audit tables, health checks, alerts.>

## N+6. Alternatives considered

| Alternative | Why not (now) |
| --- | --- |
| | |

## N+7. Risks and open questions

| # | Question | Why it matters | Owner |
| --- | --- | --- | --- |
| 1 | | | Business / Engineering / Security / Legal |

## N+8. Design review checklist

| Question | Answer | § |
| --- | --- | --- |
| How is a new <unit of extension> added without core changes? | | |
| What breaks first under load? | | |
| How do we avoid duplicate writes? | | |
| What if a dependency is down? | | |
| What does it cost to run? | | |
