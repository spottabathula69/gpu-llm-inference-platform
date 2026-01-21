# Phase 11: Production Hardening (TLS & Traffic)

[Back to README](../README.md)

## Goal
Secure the inference service with HTTPS encryption and protect availability using Rate Limiting.

## 1. TLS Encryption (HTTPS)
We implemented TLS termination at the Ingress layer using **cert-manager**.
- **Issuer**: Self-Signed `ClusterIssuer` (for local Minikube validation).
- **Certificate**: `vllm-tls` (auto-generated).
- **Endpoint**: `https://llm.local/v1/...`

### Verification
- `curl -k https://llm.local...` returns 200 OK.
- Browser/Client connects via port 443 secure channel.

## 2. Traffic Control (Rate Limiting)
We configured **NGINX Ingress** annotations to throttle aggressive clients to prevent Denial of Service (DoS).

| Setting | Value | Description |
| :--- | :--- | :--- |
| `limit-rps` | **10** | Max requests per second per IP. |
| `limit-burst` | **20** | Allowed burst above the rate limit. |

### Verification
- **Test**: `k6` stress test with 20 VUs (burst load).
- **Result**: **55% Failure Rate**.
  - ~90 requests succeeded (Burst + Rate).
  - ~110 requests failed with **503 Service Temporarily Unavailable**.
- **Conclusion**: The "Noisy Neighbor" protection is active.

## Configuration Files
- **Ingress**: `infra/k8s/apps/vllm/ingress.yaml`
- **Certificates**: `infra/k8s/security/`
