import time
import json
import requests
import statistics
import argparse
import sys
import os
import numpy as np

def measure_streaming_metrics(url, model, prompt, max_tokens=256):
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.0,
        "stream": True
    }
    
    headers = {"Content-Type": "application/json"}
    # Support API Key if provided in env
    api_key = os.getenv("API_KEY", "sk-admin-token-12345") # Default to our known key for ease
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    print(f"Sending request to {url}...")
    print(f"Prompt: {prompt[:50]}...")
    
    start_time = time.time()
    first_token_time = None
    token_times = []
    
    try:
        response = requests.post(url, headers=headers, json=payload, stream=True)
        response.raise_for_status()
        
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith("data: "):
                    data_str = decoded_line[6:]
                    if data_str.strip() == "[DONE]":
                        break
                    
                    try:
                        data = json.loads(data_str)
                        # Check if this chunk actually has content (sometimes keep-alives or empty roles are sent)
                        if "choices" in data and len(data["choices"]) > 0:
                            delta = data["choices"][0].get("delta", {})
                            if "content" in delta:
                                current_time = time.time()
                                if first_token_time is None:
                                    first_token_time = current_time
                                else:
                                    token_times.append(current_time)
                    except json.JSONDecodeError:
                        pass
                        
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

    end_time = time.time()
    
    if first_token_time is None:
        print("Error: No tokens received.")
        return None

    # Calculations
    ttft = first_token_time - start_time
    total_time = end_time - start_time
    
    # Inter-Token Latencies
    itls = []
    prev_time = first_token_time
    for t in token_times:
        itls.append(t - prev_time)
        prev_time = t
        
    num_output_tokens = len(itls) + 1 # +1 for the first token
    
    # Metrics
    avg_itl = statistics.mean(itls) if itls else 0
    p95_itl = np.percentile(itls, 95) if itls else 0
    tpot = (end_time - first_token_time) / len(itls) if itls else 0 # Gen Time / (N-1) intervals
    
    metrics = {
        "ttft_s": ttft,
        "total_time_s": total_time,
        "num_tokens": num_output_tokens,
        "tokens_per_sec": num_output_tokens / total_time,
        "avg_itl_s": avg_itl,
        "p95_itl_s": p95_itl,
        "tpot_s": tpot
    }
    
    return metrics

def main():
    parser = argparse.ArgumentParser(description="Measure LLM Streaming Metrics (TTFT, ITL)")
    parser.add_argument("--url", default="http://localhost:8000/v1/chat/completions", help="Endpoint URL")
    parser.add_argument("--model", default="TinyLlama/TinyLlama-1.1B-Chat-v1.0", help="Model name")
    parser.add_argument("--max-tokens", type=int, default=256, help="Max output tokens")
    parser.add_argument("--iterations", type=int, default=5, help="Number of runs")
    args = parser.parse_args()

    print(f"\n--- Starting UX Probe ({args.iterations} iterations) ---")
    
    all_metrics = []
    
    for i in range(args.iterations):
        print(f"\nRun {i+1}/{args.iterations}")
        m = measure_streaming_metrics(
            args.url, 
            args.model, 
            "Write a short essay about the future of AI and latency.", 
            args.max_tokens
        )
        if m:
            print(f"  TTFT: {m['ttft_s']:.4f}s")
            print(f"  ITL (avg): {m['avg_itl_s']:.4f}s")
            print(f"  TPS: {m['tokens_per_sec']:.2f}")
            all_metrics.append(m)
        time.sleep(1)

    if not all_metrics:
        print("No successful runs.")
        sys.exit(1)

    # Aggregates
    avg_ttft = statistics.mean([m['ttft_s'] for m in all_metrics])
    p95_ttft = np.percentile([m['ttft_s'] for m in all_metrics], 95)
    avg_itl = statistics.mean([m['avg_itl_s'] for m in all_metrics])
    avg_tps = statistics.mean([m['tokens_per_sec'] for m in all_metrics])
    
    print("\n" + "="*40)
    print(f"FINAL RESULTS ({len(all_metrics)} runs)")
    print("="*40)
    print(f"TTFT (Time To First Token):")
    print(f"  Avg: {avg_ttft*1000:.2f} ms")
    print(f"  p95: {p95_ttft*1000:.2f} ms")
    print("-" * 20)
    print(f"TBG (Time Between Generations / ITL):")
    print(f"  Avg: {avg_itl*1000:.2f} ms")
    print("-" * 20)
    print(f"Throughput:")
    print(f"  Avg: {avg_tps:.2f} tokens/s")
    print("="*40)

if __name__ == "__main__":
    main()
