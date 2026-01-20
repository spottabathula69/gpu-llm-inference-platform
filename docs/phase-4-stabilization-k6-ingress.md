# Phase 4 — Stabilization (k6 + Ingress tuning)

[Prev: Phase 3](phase-3-investigation-stall.md) | [Next: Phase 5](phase-5-verification-results.md)


## Goal
Make load testing stable and repeatable for long generations by:
- using a more expressive load tool (`k6`) and/or
- extending ingress timeouts for generation workloads

## Key changes
### 1) Tooling switch (hey → k6)
`k6` provides:
- deterministic scenarios (iterations, VUs)
- explicit thresholds
- better error visibility and machine-readable outputs

### 2) Ingress timeouts for long responses
Increase NGINX Ingress proxy timeouts to tolerate long generation queues:

```bash
kubectl annotate ingress -n <ns> <ingress-name> \
  nginx.ingress.kubernetes.io/proxy-read-timeout="600" \
  nginx.ingress.kubernetes.io/proxy-send-timeout="600" \
  nginx.ingress.kubernetes.io/proxy-connect-timeout="30" \
  nginx.ingress.kubernetes.io/send-timeout="600" \
  --overwrite
```

Verify annotations:
```bash
kubectl describe ingress -n <ns> <ingress-name> | sed -n '/Annotations:/,/Rules:/p'
```

## Example k6 script pattern
A simple script can post a fixed JSON payload to the chat endpoint and report p95/p99:

```js
import http from 'k6/http';
import { check } from 'k6';

export const options = { vus: 4, iterations: 192 };

export default function () {
  const payload = open('loadtest/chat_long.json');
  const res = http.post('http://llm.local/v1/chat/completions', payload,
    { headers: { 'Content-Type': 'application/json' } });
  check(res, { 'status is 200': (r) => r.status === 200 });
}
```

## Why this phase matters
- Stability issues can invalidate weeks of benchmarking.
- Making the harness trustworthy is a prerequisite for tuning and for portfolio-grade benchmark artifacts.
