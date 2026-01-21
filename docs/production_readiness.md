# Production Readiness Notes (Phase 6+ / Future Work)

[Back to README](../README.md)


> These are forward-looking notes. Phase 1–5 focus on correctness + performance benchmarking/tuning. Treat this document as a backlog for “next steps” once Phase 5 is complete.

## Observability (Implemented ✅)
- **Status**: Implemented in Phase 8 via Prometheus/Grafana stack.
- **GPU metrics**: DCGM exporter is live.
- **Request metrics**: vLLM metrics (TTFT, TPOT, Queue) are visualized.
- **Next Step**: Configure **AlertManager** to Slack/PagerDuty when `vllm:num_requests_waiting > 10` or `gpu_util > 95%`.

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

## Security (Critical Next Step 🚨)
- **Authentication**: Currently, the API is open (`http://.../v1/...`). Use **OAuth2 Proxy** or an API Gateway (like Kong or Ambassador) to enforce AuthN.
- **TLS/SSL**: Terminate HTTPS at the Ingress layer using `cert-manager` and Let's Encrypt.
- **Network Policies**: Isolate the `vllm` namespace so only the Ingress Controller can talk to it.

## Autoscaling (Advanced)
- **Horizontal Pod Autoscaling (HPA)**:
  - Requires **KEDA** (Kubernetes Event-Driven Autoscaling) to scale on custom Prometheus metrics (e.g., `vllm:num_requests_waiting`).
  - *Constraint*: On single-GPU Minikube, this is purely theoretical. In Cloud (AWS/GCP), this allows infinite scaling.
- **Model Quantization**:
  - Switch to **AWQ** or **GPTQ** models (e.g., Llama-3-8B-AWQ) to fit larger models on the same RTX 3060 hardware, or increase batch size (throughput).
