# Phase 3 — Investigation (The “Stall”)

[Prev: Phase 2](phase-2-initial-load-testing-hey.md) | [Next: Phase 4](phase-4-stabilization-k6-ingress.md)


## Symptom
Under long-payload load (higher max_tokens), some runs appeared to “hang” or stop making progress, especially at certain concurrency levels.

## Evidence collected
### 1) Pod stability
- `kubectl describe pod` showed **no Events** (no OOMKills / restarts) during reproductions.

### 2) vLLM logs
- vLLM continued to accept requests and return **HTTP 200 OK**, indicating the model server was operating.

### 3) Ingress logs
- NGINX Ingress emitted **499 (Client Closed Request)** during the “stall” window.
  - Interpretation: the client/load generator closed the connection before NGINX received the upstream response.

## Root cause
The “stall” behavior was **client/harness-driven** (connection abort / timeout) rather than a vLLM deadlock.

Common contributing factors in this topology:
- Long time-to-first-byte (TTFB) under queueing/batching for generation-heavy requests.
- Ingress proxy timeouts that are too short for long generations.
- Load generator behavior (timeouts, keepalive quirks, request-count artifacts).

## Debug checklist (commands)
### Check server-side health
```bash
kubectl get pods -A -o wide | grep -E "vllm|ingress|nginx"
kubectl describe pod -n <ns> <vllm-pod> | sed -n '/Events:/,$p'
kubectl logs -n <ns> <vllm-pod> --tail=200
```

### Check ingress for client aborts/timeouts
```bash
kubectl logs -n ingress-nginx deploy/ingress-nginx-controller --tail=200
```

### Sanity-check client timeouts
- Increase client timeout for long generations.
- Prefer scripted tools that surface errors clearly (k6).

## Why this phase matters
- Prevents misdiagnosing “server deadlocks” when the root cause is client abort behavior.
- Builds an SRE-grade habit: **always correlate client errors with proxy + app logs**.
