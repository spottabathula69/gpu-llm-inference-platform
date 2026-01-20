# Production Readiness Notes (Phase 6+ / Future Work)

[Back to README](../README.md)


> These are forward-looking notes. Phase 1–5 focus on correctness + performance benchmarking/tuning. Treat this document as a backlog for “next steps” once Phase 5 is complete.

## Observability
- **GPU metrics**: DCGM exporter → Prometheus → Grafana.
- **Request metrics**: RPS, latency percentiles, queue depth, tokens/sec.
- **Logs**: structured request logs (status, latency, tokens) and error rates.

## Reliability & SLOs
- Define SLOs (e.g., p95 latency under target at chosen concurrency).
- Alert on: error rate, tail latency, GPU memory pressure, throttling.

## Autoscaling (when multi-GPU / multi-node)
- HPA/KEDA driven by queue depth and request latency.
- Consider separate pools for latency-sensitive vs batch/throughput workloads.

## Traffic management
- Rate limiting / per-tenant quotas.
- Timeouts aligned across client → ingress → service.
- Canary rollouts and safe rollback.

## Security
- AuthN/AuthZ on the inference endpoint.
- Network policies; isolate namespaces.
- Secrets management for model access tokens (if required).
