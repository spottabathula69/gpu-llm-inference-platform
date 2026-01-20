# Phase 1 — Infrastructure Setup

[Next: Phase 2](phase-2-initial-load-testing-hey.md)


## Goal
Stand up a local, production-reflective Kubernetes inference stack on **Windows + WSL2** using **Minikube (Docker driver)**, with **NVIDIA GPU scheduling** and **NGINX Ingress** routing to a vLLM service.

## What “done” looks like
- Minikube cluster running in WSL2 with Docker driver.
- NVIDIA GPU is schedulable in Kubernetes via NVIDIA device plugin.
- vLLM deployed and reachable through NGINX Ingress via `minikube tunnel`.
- Local name resolution: `llm.local -> 127.0.0.1`.

## Key steps (commands)

### 1) Start Minikube with ingress enabled
```bash
minikube start --driver=docker --container-runtime=docker --gpus=all
minikube addons enable ingress
```

### 2) Verify GPU is visible to the node runtime
On the host/WSL2 environment:
```bash
nvidia-smi
```

### 3) Install NVIDIA device plugin
Example (varies by cluster/version):
```bash
kubectl apply -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.14.5/nvidia-device-plugin.yml
```

Verify GPU becomes schedulable:
```bash
kubectl describe node | sed -n '/Capacity:/,/Allocatable:/p' | grep -i nvidia
kubectl get pods -n kube-system | grep -i nvidia
```

### 4) Deploy vLLM and expose via Ingress
- Create a Deployment that requests GPU (e.g. `resources.limits.nvidia.com/gpu: 1`).
- Create a Service for the vLLM pod.
- Create an Ingress rule mapping `llm.local` → Service.

Confirm the endpoint:
```bash
minikube tunnel
# in another terminal
curl -sS http://llm.local/v1/models
```

## Why these steps matter (interview-friendly)
- **Driver parity** (Minikube + Ingress + GPU plugin) approximates real K8s production concerns: scheduling, device plugins, and ingress proxying.
- Establishes a stable baseline for later performance work (Phase 5), where correctness and repeatability depend on a reliable platform.
