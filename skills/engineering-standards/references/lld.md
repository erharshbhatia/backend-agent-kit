# Low-level design

This file is generic and stays that way: paths are relative to the package root, and the package name, env prefix, vendors, domain words and tool names are recorded in `project-guide/knowledge/` (`STACK.md` for tools and files) and `CLAUDE.md`, never here. Language-specific idioms are in `stacks/<profile>.md`. That is what lets a project pull kit updates later (`project-bootstrap`, "Generic files stay generic").

## Contents
1. Layers and dependency rule
2. Ports and adapters
3. Composition root
4. Registries (open for extension)
5. Where does this code go?
6. Designing a new interface
7. Anti-patterns

## 1. Layers and dependency rule

```text
entrypoints (api, worker, cli)     HTTP routers, worker loops, CLI commands — thin: parse, call a use case, format
      │
application (use cases)            PlaceOrder, HandleWebhook, RunDueJobs — orchestrate ports inside a unit of work
      │
domain (pure)                      models, value objects, pure rules and policies, validation
      ▲
ports (interface types)            repositories, UnitOfWork, integration gateways, ModelClient, Notifier, Clock …
      ▲
adapters                           database repositories, HTTP integrations, model clients, template rendering, channels
```

(Use-case names above are examples from a neutral orders domain.)

- Arrows point inward: nothing in `domain` imports `application`, adapters, or any I/O library (the database driver, the HTTP client, the web framework, vendor SDKs).
- Application code calls ports, never concrete adapters.
- The layer-contract tool encodes this; its configuration is the source of truth when this text and the config disagree.

## 2. Ports and adapters

- A **port** is an interface type in the consuming package: `<module>/port` next to its consumer, or `persistence/ports/` for repositories and the unit of work. It speaks domain types only.
- An **adapter** implements one port for one technology, in its own module. Vendor SDK types never leave the adapter: translate at the edge.
- Every port that crosses a process boundary has at least two implementations over time: the real adapter and a fake or memory twin for tests. Model/LLM ports follow the project's test-policy ADR (some projects forbid fakes and test against the real model; others record fixtures). State the policy once and apply it everywhere.
- Vendor isolation (enforced): each vendor package is importable only from its adapter module; list the pairs in the layer-contract tool's configuration (the database driver only in the persistence adapter package, an LLM vendor's SDK only in its adapter module under `models/`).

## 3. Composition root

- The composition root (STACK.md names the file) builds a frozen container from the settings module. It is the only module that imports concrete adapters.
- No module-level singletons, no global clients, no environment reads outside the settings module.
- Tests build their own container with fakes and memory repositories; entrypoints build the container once.

## 4. Registries (open for extension)

- Each extensible kind of thing has a registry: handlers, integration operations (name, kind READ or WRITE, request and response models), channels, validation rules, template filters.
- Registries are populated at bootstrap from configured packages; the core never hard-codes the list.
- Adding a new kind of thing = one new module + registration + tests. If you are editing a central `match`, `switch` or `if` chain to add a case, stop and use the registry.

## 5. Where does this code go?

| You are writing… | It goes in | Talks through |
| --- | --- | --- |
| A pure business rule, policy, or validation | `domain/` | — |
| A use case (one user or system action) | `application/` | ports |
| Anything reading or writing the database | `persistence/<database>/repositories/` (the profile names the directory, e.g. `postgres/`) | its repository port |
| A call to an outside system | an integration package (`integrations/<partner>/`) as a registered operation | the integration gateway port |
| Tenant- or customer-specific behaviour | a tenant/integration package or configuration, never the core | registries, config |
| A model call | `models/` adapter | `ModelClient` port |
| HTTP endpoint / CLI command / worker loop | `entrypoints/` (thin) | a use case |
| Settings | the settings module | the container |

## 6. Designing a new interface

Write it in the design note before coding (`sdlc-workflow`):
- Name methods by intent and guarantee (`acquire_lease`, `claim_due`, `record_intent`), not mechanics (`update_row`).
- Inputs and outputs are domain types; failures are typed (`Created | Existing`, `Result`, `LeaseLost`).
- State concurrency and idempotency guarantees in the interface's documentation comment.
- List the implementations you will ship (real, fake or memory) and the contract tests they must pass.
- A change to a published port, API, event, or file format needs an ADR.

## 7. Anti-patterns

| Smell | Instead |
| --- | --- |
| Core code mentions a tenant, customer, or business-flow word | Move it to the tenant/integration package or configuration |
| `if kind == "X": ...` outside a registry | A registered handler |
| Business logic opening a database session | Return effects; the use case persists them inside one unit of work |
| A repository calling another repository or committing | The use case coordinates both inside one unit of work |
| Reading the wall clock or generating a random id inline | Injected `Clock` / `IdGenerator` |
| Catching every exception and returning null | A typed failure, or let it raise if it is a bug |
| A vendor type in a function signature outside its adapter | Translate to a domain type at the adapter edge |
| A god "service" class doing parsing, rules, and I/O | Split into entrypoint + use case + domain function + port |
| Config read deep in the call stack | Pass settings in through the container |
| Retrying a write to an outside system on timeout | Recorded-intent protocol: reconcile the unknown outcome |
