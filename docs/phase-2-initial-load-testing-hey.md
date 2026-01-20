# Phase 2 — Initial Load Testing (hey)

[Prev: Phase 1](phase-1-infrastructure-setup.md) | [Next: Phase 3](phase-3-investigation-stall.md)


## Goal
Establish early latency/throughput baselines and discover obvious bottlenecks using a simple HTTP load generator (`hey`).

## Method
- Target endpoint via Ingress:
  - `http://llm.local/v1/chat/completions`
- Use fixed JSON payloads (later standardized in Phase 5).
- Sweep concurrency: `c = 1, 2, 4, 8, 12, 16`.

## Example command
```bash
hey -n 1008 -c 8 -m POST \
  -H "Content-Type: application/json" \
  -D loadtest/chat_short.json \
  http://llm.local/v1/chat/completions
```

## Early findings
- **Short generations** scaled well as concurrency increased (throughput rose rapidly).
- **Long generations** revealed harness/timeout sensitivity (some runs appeared to “stall” or terminate early).

## Why this phase exists
- Quick, cheap baselines prevent you from “tuning blind.”
- Early harness issues are common; catching them early avoids polluted metrics later.
