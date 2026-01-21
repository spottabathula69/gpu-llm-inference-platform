#!/bin/bash
echo "Checking Ingress Connectivity..."

# Get Ingress IP
INGRESS_IP=$(kubectl get ingress -n default vllm -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
if [ -z "$INGRESS_IP" ]; then
    echo "❌ Ingress has no IP assigned. Is 'minikube tunnel' running?"
else
    echo "✅ Ingress IP: $INGRESS_IP"
fi

echo "Testing Internal Connectivity to UI (Pod Direct)..."
kubectl get pods -l app=vllm-ui -o name | xargs -I {} kubectl exec {} -- curl -s -I http://localhost:8501/_stcore/health

echo "Testing Connectivity via Host Header to $INGRESS_IP..."
curl -v -k --resolve llm.local:443:$INGRESS_IP https://llm.local/ 2>&1 | head -n 10
