import http from 'k6/http';
import { check } from 'k6';

const payloadShort = JSON.stringify({
    "model": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    "messages": [
        { "role": "system", "content": "You are a helpful assistant. Answer concisely." },
        { "role": "user", "content": "In 2 sentences, explain what Kubernetes is." }
    ],
    "max_tokens": 64,
    "temperature": 0.2,
    "stream": false
});

const payloadLong = JSON.stringify({
    "model": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    "messages": [
        { "role": "system", "content": "You are a helpful assistant. Provide a structured answer with bullet points." },
        { "role": "user", "content": "Explain how an LLM inference server works end-to-end (tokenization, prefill, decode, batching). Include operational concerns like latency, throughput, and errors." }
    ],
    "max_tokens": 256,
    "temperature": 0.2,
    "stream": false
});

export const options = {
    scenarios: {
        contacts: {
            executor: 'shared-iterations',
            vus: parseInt(__ENV.VUS) || 1,
            iterations: parseInt(__ENV.TOTAL_N) || 10,
            maxDuration: '30m',
        },
    },
    thresholds: {
        http_req_failed: ['rate<0.01'],
    },
};

export default function () {
    const url = __ENV.BASE_URL || 'http://llm.local/v1/chat/completions';
    const payloadType = __ENV.PAYLOAD_TYPE || 'short';
    const payloadStr = payloadType === 'long' ? payloadLong : payloadShort;

    const params = {
        headers: { 'Content-Type': 'application/json' },
        timeout: '600s',
    };

    const res = http.post(url, payloadStr, params);
    check(res, { 'status is 200': (r) => r.status === 200 });
}
