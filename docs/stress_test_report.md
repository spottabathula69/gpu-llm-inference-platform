# Load Test Performance Report

**Hardware Configuration**: NVIDIA GeForce RTX 3060 (Single GPU)

## Executive Summary
Load tests were conducted using `k6` (via Kubernetes Jobs) to verify system stability and performance boundaries.
The results below cover Requests Per Second (RPS), Latency (p95), and Resource Utilization.

## Short Sweep Results
| Concurrency | RPS | p95 Latency (s) | Avg GPU Util % | Max Mem (MiB) |
| :--- | :--- | :--- | :--- | :--- |
| 20 | 23.02 | 1.1310 | 55.9 | 11474.0 |
| 24 | 28.18 | 1.0371 | 55.6 | 11531.0 |
| 32 | 33.03 | 1.2501 | 54.8 | 11531.0 |
| 48 | 37.66 | 1.5463 | 53.8 | 11544.0 |
| 64 | 48.06 | 1.6137 | 51.1 | 11544.0 |

## Long Sweep Results
| Concurrency | RPS | p95 Latency (s) | Avg GPU Util % | Max Mem (MiB) |
| :--- | :--- | :--- | :--- | :--- |
| 20 | 6.52 | 3.2544 | 74.4 | 11522.0 |
| 24 | 7.87 | 3.2147 | 73.7 | 11529.0 |
| 32 | 9.39 | 3.5629 | 72.9 | 11529.0 |
| 48 | 12.42 | 4.0375 | 71.9 | 11529.0 |
| 64 | 14.93 | 4.3719 | 66.7 | 11529.0 |

## Production Readiness Guide
### 1. Observability
- **Metrics**: Deploy `dcgm-exporter` to scrape GPU metrics into Prometheus. Dashboard via Grafana.
- **Tracing**: Integrate OpenTelemetry sidecar for request-level tracing (e.g. Jaeger) to pinpoint latency bottlenecks.
### 2. Autoscaling
- **HPA**: Use Kubernetes HPA with custom metrics (e.g., `avg_gpu_util > 85%` or `requests_per_second`).
- **KEDA**: Event-driven autoscaling based on queue depth (e.g. Kafka/RabbitMQ) if using async inference.
### 3. Traffic Management
- **Ingress**: Nginx Ingress Controller (current) is suitable. For advanced routing (canary/blue-green), consider Gateway API + Istio.
### 4. Load Testing
- **Tools**: `hey` is good for quick baselines. For realistic scenarios, use `Locust` (Python) or `k6` (JS) to simulate user sessions and variable wait times.
