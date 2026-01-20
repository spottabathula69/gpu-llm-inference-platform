# Phase 8: Observability Implementation

[Back to README](../README.md)

## Goal
Transform the system from a "Black Box" to a "Glass Box" using **Prometheus** and **Grafana** to visualize real-time performance and hardware metrics.

## Components Implemented
1.  **Prometheus Stack**: `kube-prometheus-stack` (Helm) deployed in `monitoring` namespace.
2.  **vLLM Metrics**: Scraped via `ServiceMonitor` on port `8000` (endpoint `/metrics`).
3.  **GPU Metrics**: NVIDIA **DCGM Exporter** deployed as a DaemonSet to expose `DCGM_FI_DEV_GPU_UTIL` and memory stats.
4.  **Grafana Dashboard**: Custom dashboard showing:
    - **Traffic**: Requests/sec (Running vs Waiting).
    - **Memory**: GPU KV Cache Usage %.
    - **Latency**: Time-To-First-Token (TTFT) and Time-Per-Output-Token (TPOT) p95 histograms.

## Configuration Details
- **Namespace**: `monitoring`
- **Port Forwarding**: Grafana is accessed via `kubectl port-forward svc/prometheus-grafana -n monitoring 3000:80`.
- **Credentials**: `admin` / `admin`.

## Verification
- Validated that `vllm:num_requests_running` spikes during `make benchmark`.
- Validated that `dcgm_gpu_utilization` correlates with stress tests.
- Captured TTFT metrics using the streaming probe (`loadtest/ttft_probe.py`).

## Screenshots
*(Refer to README for dashboard visualization)*
