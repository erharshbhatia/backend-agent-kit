# Back-of-the-envelope estimates

The goal is not precision. It is to find which resource runs out first, by roughly how much headroom we have, and which design choices the numbers force or rule out. Every number is either a stated requirement or a visible assumption.

## Contents
1. Method
2. Traffic
3. Concurrency (Little's law)
4. External integrations
5. LLM tokens and cost
6. Storage
7. Database throughput
8. Compute
9. Sensitivity: what breaks first
10. Reference numbers

## 1. Method

1. **Inputs table first.** One row per parameter: `Parameter | Value | Basis`. Basis is `Requirement` or `Assumption: <why>`. Never bury an assumption inside a calculation.
2. **Derive, don't guess.** Each derived row is `Quantity | Calculation | Result`, with the arithmetic shown so a reviewer can redo it.
3. **Design for peak, cost for average.** Size capacity at the peak design point (plus burst); compute daily volume, storage, and cost from the average.
4. **Round and add margin.** Round results to one or two significant figures; state the design target separately ("≈ 720 → design for 1,000").
5. **Conclude.** End with what the numbers rule in and out, and the binding constraints in order.
6. **Revisit.** When a benchmark or production number replaces an assumption, update the input row and note the source and date.

## 2. Traffic

| Quantity | Calculation |
| --- | --- |
| Average rate | peak × average-to-peak ratio (0.2–0.3 is typical for peaky human traffic) |
| Daily requests | average/s × 86,400 |
| Burst | peak × burst factor for a stated duration (incidents, campaigns, due dates) |
| Sessions per day | daily requests ÷ requests per session |
| New sessions per second at peak | peak ÷ requests per session |

## 3. Concurrency (Little's law)

`in-flight = arrival rate × time in system`.

| Use | Example (sample domain: an order-tracking chat) |
| --- | --- |
| In-flight requests | 120 req/s × 2.5 s processing ≈ 300 → design for 500 |
| Concurrent sessions | 12 new sessions/s × 600 s session ≈ 7,200 |
| In-flight external calls | 220 calls/s × 0.8 s ≈ 180 |
| Concurrent LLM calls | 180 req/s × 1.2 s ≈ 220 → design for 300 |

These numbers size connection pools, worker concurrency, and provider rate limits; they matter more than CPU for I/O-bound services.

## 4. External integrations

| Quantity | Calculation |
| --- | --- |
| Raw peak calls | peak requests × calls per request |
| After cache | raw × (1 − hit rate); only for data with declared freshness |
| Storm load | after-cache × burst factor |
| In-flight | calls/s × latency |

Compare against what the external system is provisioned for. Back-office systems are often the first thing to break; if so, the design needs bulkheads, coalescing, caching, rate limits, and short-circuiting.

## 5. LLM tokens and cost

| Quantity | Calculation |
| --- | --- |
| Peak LLM requests | peak requests × LLM calls per request (0 for deterministic paths) |
| Peak input tokens/min | requests/s × input tokens × 60 |
| Peak output tokens/s | requests/s × output tokens |
| Daily tokens | average/s × calls × tokens × 86,400 |
| Effective input with prompt cache | tokens × (1 − cached share) + tokens × cached share × cache price ratio |
| Daily cost | effective input × input rate + output × output rate |

State the rates as placeholders until contracted. Usual conclusion: the LLM is the dominant variable cost and the tightest external rate limit. List the levers in order of impact (skip the model on deterministic paths; smaller model per task after evals; static-prefix-first prompts for cache hits; per-call token budgets). Peak tokens/min against the provider's quota is an open question with an owner.

## 6. Storage

One row per data class: `Data | Size per item | Daily volume | Retention | Total`.

- Split hot current-state tables from append-only logs; logs dominate growth.
- Include indexes (often 30–100% on top of rows), WAL, backups, and replicas.
- Name the retention policy and the partitioning plan for anything that grows without bound.

## 7. Database throughput

| Quantity | Calculation |
| --- | --- |
| Writes/s at peak | requests/s × writes per request (count every insert/update the hot path makes) |
| Reads/s at peak | requests/s × reads per request |
| WAL volume | writes/s × average row size |
| Connections | processes × (pool + overflow + dedicated connections) ≤ `max_connections` − reserved |

Rules of thumb: a well-provisioned single Postgres primary handles low thousands of small writes/s with headroom; revisit distributed storage only at 5–10× that. Connection count usually becomes a limit before throughput does.

## 8. Compute

`CPU = requests/s × CPU ms per request`. Measure CPU per request with a benchmark as soon as the hot path exists and replace the assumption. I/O-bound services are sized by concurrency and availability (N+1 across zones), not CPU.

## 9. Sensitivity: what breaks first

Change one input at a time to a plausible extreme and find the first resource to run out:

| If this changes | First thing to break | Mitigation already in design |
| --- | --- | --- |
| Peak ×2 sustained | | |
| External calls per request ×2 | | |
| LLM calls per request ×2 | | |
| Burst ×5 on one feature | | |
| Average-to-peak ratio → 1 | storage and cost ×4 | partitioning, archive |

If a row has no mitigation, it becomes a risk in Open questions.

## 10. Reference numbers

| Thing | Order of magnitude |
| --- | --- |
| Seconds per day | 86,400 |
| Same-region network round trip | ~0.5–1 ms |
| Postgres small indexed read / single-row write (commit) | ~0.1–1 ms / ~1–5 ms |
| Typical back-office API latency | 100 ms–2 s |
| Small LLM call latency | ~0.5–2 s; large reasoning call 5–60 s |
| One Python async API process (DB-bound, no LLM) | tens to low hundreds of requests/s; benchmark it |
| Postgres default `max_connections` | 100 (3 reserved) |

Replace these with measured numbers as soon as you have them, and cite the benchmark.
