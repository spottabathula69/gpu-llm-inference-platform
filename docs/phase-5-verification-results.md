# Phase 5 — Verification & Results (Baseline)

[Prev: Phase 4](phase-4-stabilization-k6-ingress.md) | [Full report](load_test_report.md)


[Prev: Phase 4](phase-4-stabilization-k6-ingress.md) | [Load Test Report](load_test_report.md)


## Goal
Run a full, repeatable performance matrix and capture:
- Requests/sec (throughput)
- p95 latency (tail)
- Error-free correctness (no 4xx/5xx)
- GPU utilization and GPU memory footprint

## Workload
- Endpoint: `http://llm.local/v1/chat/completions` (NGINX Ingress)
- Payloads:
  - Short: `max_tokens=64`
  - Long: `max_tokens=256`
- Concurrency sweep: `1, 2, 4, 8, 12, 16`
- GPU monitoring: `nvidia-smi` sampled at 1s intervals

## Results — Short sweep (64 tokens)
| Concurrency | RPS  | p95 latency (s) | Avg GPU util % | Max mem (MiB) |
| :---: | :---: | :---: | :---: | :---: |
| 1  | 1.71  | 0.6477 | 79.1 | 5978 |
| 2  | 3.04  | 0.7028 | 78.5 | 5992 |
| 4  | 5.93  | 0.6978 | 75.5 | 5992 |
| 8  | 10.98 | 0.7794 | 75.3 | 5989 |
| 12 | 15.76 | 1.1165 | 71.4 | 5989 |
| 16 | 20.18 | 0.9548 | 66.5 | 5970 |

## Results — Long sweep (256 tokens)
| Concurrency | RPS  | p95 latency (s) | Avg GPU util % | Max mem (MiB) |
| :---: | :---: | :---: | :---: | :---: |
| 1  | 0.43 | 2.4615 | 81.8 | 5972 |
| 2  | 0.78 | 2.6726 | 84.9 | 5956 |
| 4  | 1.51 | 2.7778 | 83.1 | 5944 |
| 8  | 2.93 | 2.8377 | 80.7 | 5943 |
| 12 | 4.27 | 3.0346 | 80.6 | 5938 |
| 16 | 5.47 | 3.0932 | 76.6 | 5938 |

## Interpretation (baseline)
- **Short**: throughput scales strongly with concurrency; tail latency increases at higher concurrency due to queueing.
- **Long**: workload is compute-bound; p95 grows slowly as concurrency rises (queue depth increases), while RPS increases substantially.
- **GPU memory** remained ~5.9–6.0GB, leaving headroom on a 12GB card for tuning (e.g., increasing `gpu-memory-utilization`).

## Next (Phase 5 tuning)
Apply low-risk tuning knobs (example):
- increase `--gpu-memory-utilization`
- increase `--max-num-seqs`

Then re-run the exact same matrix to compare deltas.
