# Production Readiness Notes (Phase 6+ / Future Work)

[Back to README](../README.md)


> These are forward-looking notes. Phase 1–5 focus on correctness + performance benchmarking/tuning. Treat this document as a backlog for “next steps” once Phase 5 is complete.

## Observability (Implemented ✅)
- **Status**: Implemented in Phase 8 via Prometheus/Grafana stack.
- **GPU metrics**: DCGM exporter is live.
- **Request metrics**: vLLM metrics (TTFT, TPOT, Queue) are visualized.
- **Next Step**: Configure **AlertManager** to Slack/PagerDuty when `vllm:num_requests_waiting > 10` or `gpu_util > 95%`.

## Reliability & SLOs (Implemented ✅)
- **Status**: Implemented in Phase 10 via `PrometheusRule`.
- **Alerts**: Active for High Latency (TTFT > 200ms), Saturation (Queue > 20), and Errors.
- **Next Step**: Configure AlertManager receivers (Slack/PagerDuty).

## Traffic management
- **Rate Limiting**: Configure NGINX Ingress to limit RPS per IP to prevent DoS.
- **Timeouts**: Align client/proxy timeouts (currently 600s).

## Security
- **Authentication (Implemented ✅)**: API Key enforcement is active (Phase 9).
- **TLS/SSL (Next Step)**: Terminate HTTPS at the Ingress layer using `cert-manager`.
- **Network Policies**: Isolate the `vllm` namespace.

## Autoscaling (Advanced)
- **Horizontal Pod Autoscaling (HPA)**:
  - Requires **KEDA** (Kubernetes Event-Driven Autoscaling) to scale on custom Prometheus metrics (e.g., `vllm:num_requests_waiting`).
  - *Constraint*: On single-GPU Minikube, this is purely theoretical. In Cloud (AWS/GCP), this allows infinite scaling.
- **Model Quantization**:
  - Switch to **AWQ** or **GPTQ** models (e.g., Llama-3-8B-AWQ) to fit larger models on the same RTX 3060 hardware, or increase batch size (throughput).
