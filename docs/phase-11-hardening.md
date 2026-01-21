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

### Verification Results
#### 1. Rate Limiting Test
- **Command**: `k6 run ... -e VUS=20 -e ITERATIONS=200`
- **Goal**: Exceed 10 RPS limit with 20 concurrent users.
- **Result**:
  - **Success**: 90 requests (45%) - Allowed within burst/rate.
  - **Blocked**: 110 requests (55%) - Rejected with `503 Service Unavailable`.
- **Status**: ✅ Verified (DoS Protection Active).

#### 2. HTTPS Access
- **Command**: `curl -k -I https://llm.local/v1/models`
- **Result**: `HTTP/2 200` (Encrypted connection).
- **Status**: ✅ Verified.

## Configuration Files
- **Ingress**: `infra/k8s/apps/vllm/ingress.yaml`
- **Certificates**: `infra/k8s/security/`
