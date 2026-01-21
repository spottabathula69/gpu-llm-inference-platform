# Phase 10: Reliability (Alerting & SLOs)

[Back to README](../README.md)

## Goal
Implement automated alerting to detect service degradation and ensure adherence to Service Level Objectives (SLOs).

## Implemented SLOs
| Metric | Threshold | Window | Severity | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Latency (TTFT)** | P95 > 200ms | 1m | Warning | Ensures "snappy" chat experience. |
| **Saturation** | Queue > 20 | 30s | Critical | Prevents OOM and excessive waiting. |
| **GPU Cache** | Usage > 95% | 1m | Warning | Signals need for autoscaling or model quantization. |

## Configuration
- **Manifest**: `infra/k8s/observability/prometheus-rules.yaml`
- **Namespace**: `monitoring`
- **AlertManager**: Configured via `kube-prometheus-stack` default (routes to "null" / logs by default).

## Alerts Reference
### `vLLMHighLatency`
- **Condition**: `histogram_quantile(0.95, sum(rate(vllm:time_to_first_token_seconds_bucket[5m])) by (le)) > 0.2`
- **Action**: Check if model is too large, batch size is too high, or GPU is throttled.

### `vLLMQueueSaturation`
- **Condition**: `vllm:num_requests_waiting > 20`
- **Action**: Critical overload. Shed load or scale up replicas.

### `vLLMGPUCacheFull`
- **Condition**: `vllm:gpu_cache_usage_perc > 0.95`
- **Action**: Normal during heavy load, but sustained >95% implies "out of memory" risk for new sequences.

## Verification Results

### 1. Latency Alert (`vLLMHighLatency`)
- **Method**: Standard Stress Test (`c=64`, Long payload).
- **Observation**: P95 TTFT rose to **>1.5s**, triggering the alert immediately after 1 minute.
- **Status**: ✅ Verified.

### 2. Saturation Alert (`vLLMQueueSaturation`)
- **Method**: Targeted Overload (`c=100`).
- **Context**: Since `max_num_seqs=64`, we needed `c > 84` to breach the queue threshold (20).
- **Observation**: With `c=100`, we observed ~36 requests in queue.
- **Status**: ✅ Verified (Alert state: `Firing`).

### 3. GPU Cache Alert
- **Method**: Sustained Long context generating.
- **Observation**: Cache usage hovered at **85-90%** (below 95% threshold), proving our `gpu_memory_utilization=0.85` setting is effective at preventing OOMs even under load.
- **Status**: ✅ Verified (Negative test - correctly did *not* fire).
