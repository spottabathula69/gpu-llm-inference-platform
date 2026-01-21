# Phase 13: Model Quantization (Llama-3-8B on Consumer Hardware)

[Back to README](../README.md)

## Goal
Run a **State-of-the-Art 8B Parameter Model** (Llama 3) on a single consumer GPU (RTX 3060, 12GB VRAM).
Standard FP16 inference for 8B models requires ~16GB VRAM, which is impossible on this hardware. We used **AWQ (Activation-aware Weight Quantization)** to fit the model.

## Implementation
We deployed `casperhansen/llama-3-8b-instruct-awq` (4-bit Quantization).

### Configuration
- **Deployment**: `infra/k8s/apps/vllm/deployment_llama8B.yaml`
- **Engine Args**:
  - `--quantization awq`: Enables the AWQ kernel.
  - `--dtype half`: Uses FP16 for activations.
  - `--max-model-len 4096`: Limits context window to save KV Cache memory.
  - `--gpu-memory-utilization 0.95`: Maximizes VRAM usage (~11GB).
- **Resources**:
  - `memory: 16Gi` (CPU Limit): Required for loading weights.

## Results
| Metric | Value | Notes |
| :--- | :--- | :--- |
| **Model Size (FP16)** | ~16 GB | ❌ Impossible on 12GB Card |
| **Model Size (AWQ)** | **~5.5 GB** | ✅ Fits easily |
| **KV Cache Space** | ~5.5 GB | Room for ~2300 blocks (Context) |
| **Total VRAM Used** | **11.1 GB** | 92% Utilization |

### Verification
- **Command**: `kubectl logs -l variant=llama-8b`
- **Output**:
  ```text
  Loading model weights took 5.3440 GB
  # GPU blocks: 2302
  Maximum concurrency: 8.99x
  ```

## Conclusion
We successfully upgraded the platform from a "Toy" 1.1B model to a "Production" 8B model by leveraging 4-bit quantization, proving **significant cost efficiency** (running SOTA models on cheap hardware).
