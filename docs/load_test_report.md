# Load Test Report (Baseline)

[Back to Phase 5](phase-5-verification-results.md) | [Production Readiness Notes](production_readiness.md)


This report summarizes throughput (RPS), tail latency (p95), and GPU metrics for short (64-token) and long (256-token) chat completions.

## Environment
- GPU: NVIDIA GeForce RTX 3060 (12GB)
- Kubernetes: Minikube (Docker driver) in WSL2
- Ingress: NGINX Ingress via `minikube tunnel`
- Endpoint: `http://llm.local/v1/chat/completions`

## Results — Short sweep (64 tokens)
| Concurrency | RPS  | p95 latency (s) | Avg GPU util % | Max mem (MiB) |
| :---: | :---: | :---: | :---: | :---: |
| 1  | 1.71  | 0.6477 | 79.1 | 5978 |
| 2  | 3.04  | 0.7028 | 78.5 | 5992 |
| 4  | 5.93  | 0.6978 | 75.5 | 5992 |
| 8  | 10.98 | 0.7794 | 75.3 | 5989 |
| 12 | 15.76 | 1.1165 | 71.4 | 5989 |
| 16 | 20.18 | 0.9548 | 66.5 | 5970 |

### Notes
- Throughput increases with concurrency.
- Tail latency increases once queueing dominates (notably at c=12+).

## Results — Long sweep (256 tokens)
| Concurrency | RPS  | p95 latency (s) | Avg GPU util % | Max mem (MiB) |
| :---: | :---: | :---: | :---: | :---: |
| 1  | 0.43 | 2.4615 | 81.8 | 5972 |
| 2  | 0.78 | 2.6726 | 84.9 | 5956 |
| 4  | 1.51 | 2.7778 | 83.1 | 5944 |
| 8  | 2.93 | 2.8377 | 80.7 | 5943 |
| 12 | 4.27 | 3.0346 | 80.6 | 5938 |
| 16 | 5.47 | 3.0932 | 76.6 | 5938 |

### Notes
- Long generation is compute-heavy; even at low concurrency, GPU utilization is high.
- Increasing concurrency increases throughput, with a gradual increase in p95 latency.

## Repro commands (example)
GPU monitoring:
```bash
nvidia-smi --query-gpu=timestamp,utilization.gpu,utilization.memory,memory.used,memory.total,temperature.gpu,power.draw \
  --format=csv -l 1 | tee loadtest/gpu_logs/run_$(date +%Y%m%d_%H%M%S).csv
```

Load test (example):
```bash
hey -n <N> -c <C> -m POST \
  -H "Content-Type: application/json" \
  -D loadtest/chat_long.json \
  http://llm.local/v1/chat/completions
```
