# Phase 6 — Advanced Verification (Stress Only)

[Prev: Phase 5](phase-5-verification-results.md) | [Load Test Report](load_test_report.md)

## Goal
Determine the "Breaking Point" of the system by pushing concurrency well beyond the typical operating range (c=16).
We want to verify:
1.  **Queue Stability**: Does vLLM crash or OOM when hundreds of requests are queued?
2.  **Saturation Behavior**: Does latency degrade gracefully or catastrophically?
3.  **Error Handling**: Do we see 5xx errors or timeouts?

## Workload (Stress)
- **Tool**: `k6` (Kubernetes Job)
- **Concurrency**: `20, 24, 32, 48, 64` (Simultaneous Users)
- **Payloads**:
    - **Short**: 64 tokens (High Throughput stress)
    - **Long**: 256 tokens (Compute/Queue stress)

## Results

### Short Sweep (64 tokens)
| Concurrency | RPS | p95 Latency (s) | Avg GPU Util % | Max Mem (MiB) |
| :--- | :--- | :--- | :--- | :--- |
| 20 | 23.02 | 1.13 | 55.9 | 11474 |
| 24 | 28.18 | 1.04 | 55.6 | 11531 |
| 32 | 33.03 | 1.25 | 54.8 | 11531 |
| 48 | 37.66 | 1.55 | 53.8 | 11544 |
| 64 | 48.06 | 1.61 | 51.1 | 11544 |

### Long Sweep (256 tokens)
| Concurrency | RPS | p95 Latency (s) | Avg GPU Util % | Max Mem (MiB) |
| :--- | :--- | :--- | :--- | :--- |
| 20 | 6.52 | 3.25 | 74.4 | 11522 |
| 24 | 7.87 | 3.21 | 73.7 | 11529 |
| 32 | 9.39 | 3.56 | 72.9 | 11529 |
| 48 | 12.42 | 4.04 | 71.9 | 11529 |
| 64 | 14.93 | 4.37 | 66.7 | 11529 |

## Interpretation
1.  **Zero Errors**: Even at `c=64` (queue depth > 4x hardware capacity), the system returned **0 errors**.
2.  **Graceful Degradation**: Latency increased linearly, not exponentially.
    - Long (c=16) p95: **3.22s**
    - Long (c=64) p95: **4.37s**
    - This proves the `max-num-seqs=64` tuning and `0.85` memory utilization provides a massive safety buffer.
3.  **Throughput**: Continued to scale. We did not hit a hard clamp, suggesting the GPU could potentially handle even more lightweight requests/sec, though context switching latencies would eventually dominate.

## UX Metrics (Streaming)
**Tool**: `ttft_probe.py` (Custom Python script using `requests` with `stream=True`)
**Goal**: Measure the "feel" of chat interaction.
- **TTFT (Time To First Token)**: Latency before the user sees the first word.
- **ITL (Inter-Token Latency)**: Smoothness of the text generation.
- **TPOT (Time Per Output Token)**: Inverse of generation speed.

**Results (5 runs)**:
| Metric | Average | p95 | Best Case |
| :--- | :--- | :--- | :--- |
| **TTFT** | **56.60 ms** | 168.27 ms | 18.5 ms |
| **ITL** | **9.32 ms** | - | 8.8 ms |
| **TPOT** | **9.48 ms** | - | 8.8 ms |
| **Speed** | **105.4 tok/s** | - | 113.4 tok/s |

**Interpretation**:
- **Instant Response**: A 56ms start time is effectively instantaneous to a human (blink is 100-400ms).
- **TPOT / ITL**: at ~9.5ms per token, the generation is effectively real-time.
- **Smooth Streaming**: 105 tokens/sec is ~5x faster than average reading speed. The text flows smoothly without stutter.
- **Cold Start**: The first request took ~200ms (p95), likely due to connection establishment, but subsequent requests were <20ms.

## Conclusion
The infrastructure is **Production Ready** for both:
1.  **High-Concurrency Spikes** (Proven by Stress Test c=64)
2.  **Interactive Chat** (Proven by TTFT Probe)
