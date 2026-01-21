#!/bin/bash
echo "Verifying Llama-3-8B-AWQ Inference..."
# Use -k for self-signed certs
curl -k -s https://llm.local/v1/chat/completions \
  -H "Authorization: Bearer sk-admin-token-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "casperhansen/llama-3-8b-instruct-awq",
    "messages": [
      {"role": "user", "content": "Who made you and what model version are you?"}
    ],
    "max_tokens": 100
  }' | jq
