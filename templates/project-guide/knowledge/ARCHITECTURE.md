# Architecture (summary of `tech-doc.md`; details there)

<!-- Fill-in template. A one-page summary an agent can read in two minutes. Point to the HLD section for each item instead of copying it. Update in the same change whenever a component, deployable, data flow, or table group changes. -->

## Layers, top to bottom

<!-- Describe the request path from outside in. Example shape: -->

1. **Clients and outside systems** → **edge** (HTTP API, webhook intake, channel adapters).
2. **Application** (`<package>/application`): use cases that orchestrate ports.
3. **Domain** (`<package>/domain`): pure models and rules.
4. **Gateways** (libraries behind ports): integrations with outside systems, model clients, notifications.
5. **State**: <one relational database, schema `<schema>`>; <queues, caches, object storage if any>.

## Core model

<!-- The central concepts of this system and how they relate (the nouns in GLOSSARY.md). One short paragraph or a list. -->

## Runtime

<!-- How work moves: synchronous request path vs background work, how background work is claimed (leases, atomic claims), how it resumes after a crash, how processes are woken (database notifications, polling). HLD section: <§N>. -->

## Writes to outside systems

<!-- The recorded-intent protocol as this project implements it: where intent is stored, the idempotency key, how unknown outcomes are reconciled. -->

## Models (if any)

<!-- Which model tiers exist, which use cases call them, the test policy ADR. -->

## Data

<!-- Table groups and what each holds; the binding spec is `implementation/database-schema.md`. -->

| Area | Tables | Written by |
| --- | --- | --- |
| <area> | <tables> | <process> |

## Deployables

| Process | Entry point | Takes traffic? | Scales by |
| --- | --- | --- | --- |
| api | <entry point, as STACK.md names it> | yes | CPU, request latency |
| worker | `<cli> worker` | no | backlog of claimed work |
| migrate (job) | <migration tool> upgrade to head | no | — |
