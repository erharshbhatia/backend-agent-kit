# Debugging

Start from IDs and the audit tables, not from logs. Every request and background job binds its IDs (`<request_id>`, `<aggregate>_id`, `<job>_id`, `<external_call>_id`) into every log line and audit row, so one ID leads to the whole story.

<!-- Fill-in template. The generic entries below apply to any service built with this kit; replace the placeholders with this project's tables and commands, and add a "Common signatures" row every time a new failure pattern is found (the change record links it). -->

## Where to look

| Question | Look at |
| --- | --- |
| What did this request or job do, in order? | The step/audit log table for the aggregate, ordered by sequence |
| Where is it now, and what is it waiting for? | The aggregate's `status`, its lease columns (`lease_owner`, `lease_expires_at`), wait/timer tables |
| Did an inbound event arrive? Was it matched? | The event inbox (status matched / unmatched), correlation table, pending signals |
| What did an external call send and receive? | The recorded-intent table (request/response evidence, status, error category, idempotency key) |
| Why did a decision go that way? | The decision/audit table (policy, version, inputs, matched rule) |
| What did a model see and return? | The model-call audit table (model, prompt ref, tokens, finish reason, redacted payloads) |
| Did the reply or notification go out? | The outbox (status, attempts, last error) |
| Is a background process alive? | Its heartbeat / last tick log line, recovery sweeps, expired leases |

Locally: `<cli> <aggregate> show <id>` prints the timeline (add such a command early; it pays for itself).

## Reproduce before fixing

1. Write a failing test at the lowest layer that shows the bug: domain unit test, application test with memory repositories and fakes, or an end-to-end scenario.
2. Confirm it fails for the reported reason, not some other one.
3. Fix, keep the test as a regression test, and cite the bug in its name or docstring.

Follow the project's model test policy ADR for reproductions that reach a model. Outside systems stay mocked; clock, IDs and storage keep their test doubles.

## Common signatures

| Symptom | Likely cause |
| --- | --- |
| Lease lost / version conflict on save | Another process took the work (slow step, lease too short, or a real race); check lease extension during long external calls |
| Work stuck `RUNNING` | Process died; the recovery sweep should resume it after lease expiry; check the sweep runs |
| Work stuck waiting for an event | Event never matched: compare the inbox correlation key with the registered correlation |
| Duplicate external effect | Idempotency key not stable (random part, missing business id) or the recorded-intent protocol bypassed |
| Test passes alone, fails in the suite | Shared state: a module-level singleton, an unfrozen clock, or a reused database |
| <symptom> | <cause and where to check> |

### Postgres

| Symptom | Likely cause |
| --- | --- |
| Notifications from LISTEN/NOTIFY never arrive | Connection goes through a transaction-mode pooler; LISTEN needs a direct or session-mode connection |
| `too many clients already` | Sum of per-process pools exceeds `max_connections`; see the connection budget in the HLD |
