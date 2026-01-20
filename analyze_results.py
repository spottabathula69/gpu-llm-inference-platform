
import os
import re
import csv
import glob
from datetime import datetime, timedelta

import json
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Analyze Load Test Results")
    parser.add_argument("--k6-dir", default="loadtest/logs/k6", help="Directory containing k6 JSON logs")
    parser.add_argument("--gpu-dir", default="loadtest/logs/gpu", help="Directory containing GPU CSV logs")
    parser.add_argument("--output", default="docs/load_test_report.md", help="Output Markdown report path")
    return parser.parse_args()

def parse_k6_output(filepath):
    """Parses k6 JSON summary to extract RPS and p95 latency."""
    data = {}
    try:
        with open(filepath, 'r') as f:
            description = f.read()
            # Brute force finder for valid JSON block containing 'metrics'
            summary = None
            candidates = [pos for pos, char in enumerate(description) if char == '{']
            for pos in candidates:
                try:
                    # Attempt to parse from this brace to end
                    # (JSON parser stops at valid end usually, or we can assume it goes to EOF)
                    # json.loads parses the *whole string*? No, it expects valid JSON.
                    # If content has trailing garbage, loads fails.
                    # K8s logs might have trailing close lines?
                    # But 'cat' was last.
                    pot_json = description[pos:]
                    obj = json.loads(pot_json)
                    if 'metrics' in obj:
                        summary = obj
                        break
                except json.JSONDecodeError:
                    continue
            
            if not summary:
                print(f"No valid JSON found in {filepath}")
                return data

            # k6 structure: metrics -> http_reqs -> count / rate
            # metrics -> http_req_duration -> p(95)
            
            # RPS
            # k6 "rate" in summary is often reqs/s
            if 'metrics' in summary and 'http_reqs' in summary['metrics']:
                # values.rate is hits/second
                # Check if 'values' exists (old) or direct (new)
                if 'values' in summary['metrics']['http_reqs']:
                    data['rps'] = summary['metrics']['http_reqs']['values']['rate']
                else:
                    data['rps'] = summary['metrics']['http_reqs'].get('rate', 0)
            
            # p95 Latency (ms -> s)
            if 'metrics' in summary and 'http_req_duration' in summary['metrics']:
                 # values['p(95)'] is in ms
                 metric = summary['metrics']['http_req_duration']
                 if 'values' in metric:
                     p95_ms = metric['values'].get('p(95)', 0)
                 else:
                     p95_ms = metric.get('p(95)', 0)

                 data['p95'] = p95_ms / 1000.0
                 
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
    return data

def parse_gpu_log_lines(filepath):
    """Parses nvidia-smi CSV log lines."""
    records = []
    try:
        with open(filepath, 'r') as f:
            reader = csv.reader(f)
            header = next(reader, None) # Skip header
            for row in reader:
                if not row: continue
                # timestamp, utilization.gpu [%], utilization.memory [%], memory.used [MiB], memory.total [MiB], ...
                try:
                    ts_str = row[0].strip()
                    # format: 2026/01/18 21:52:29.123
                    ts = datetime.strptime(ts_str.split('.')[0], "%Y/%m/%d %H:%M:%S")
                    
                    util_gpu = float(row[1].replace(' %', '').strip())
                    mem_used = float(row[3].replace(' MiB', '').strip())
                    
                    records.append({
                        'timestamp': ts,
                        'util_gpu': util_gpu,
                        'mem_used': mem_used
                    })
                except ValueError:
                    continue
    except Exception as e:
        print(f"Error parsing GPU log {filepath}: {e}")
    return records

def analyze_sweep(sweep_type, log_dir, gpu_dir, gpu_log_pattern):
    print(f"\nAnalyzing {sweep_type} sweep results...")
    
    # Find all GPU logs
    gpu_logs = glob.glob(os.path.join(gpu_dir, gpu_log_pattern))
    if not gpu_logs:
        print(f"No GPU log found for {sweep_type} sweep in {gpu_dir}/{gpu_log_pattern}")
        return

    # Load and concat all GPU logs
    all_gpu_records = []
    for log in gpu_logs:
        all_gpu_records.extend(parse_gpu_log_lines(log))
    
    # Sort by timestamp
    all_gpu_records.sort(key=lambda x: x['timestamp'])
    
    if not all_gpu_records:
        print("No valid GPU log records loaded.")
        return
        
    print(f"Loaded {len(all_gpu_records)} GPU stats entries.")

    results = []
    # k6 outputs: {payload}_c{c}_summary.json
    result_files = glob.glob(os.path.join(log_dir, f'{sweep_type}_c*_summary.json'))
    
    for filepath in sorted(result_files):
        filename = os.path.basename(filepath)
        c_match = re.search(r'_c(\d+)_', filename)
        if not c_match:
            continue
        c = int(c_match.group(1))
        
        metrics = parse_k6_output(filepath)
        
        mtime = os.path.getmtime(filepath)
        end_time = datetime.fromtimestamp(mtime)
        start_time = end_time - timedelta(seconds=120) # Approx window
        
        relevant_records = [
            r for r in all_gpu_records 
            if start_time <= r['timestamp'] <= end_time
        ]
        
        avg_gpu = 0
        max_mem = 0
        if relevant_records:
            avg_gpu = sum(r['util_gpu'] for r in relevant_records) / len(relevant_records)
            max_mem = max(r['mem_used'] for r in relevant_records)
            
        results.append({
            'concurrency': c,
            'rps': metrics.get('rps', 0),
            'p95_latency': metrics.get('p95', 0),
            'avg_gpu_util': avg_gpu,
            'max_mem_used': max_mem
        })

    # Print table
    print(f"{'Concurrency':<12} {'RPS':<10} {'p95 Latency':<12} {'Avg GPU %':<10} {'Max Mem (MiB)':<15}")
    print("-" * 65)
    for r in sorted(results, key=lambda x: x['concurrency']):
        print(f"{r['concurrency']:<12} {r['rps']:<10.2f} {r['p95_latency']:<12.4f} {r['avg_gpu_util']:<10.1f} {r['max_mem_used']:<15.1f}")

    return sorted(results, key=lambda x: x['concurrency'])

def generate_report(results, output_file="docs/load_test_report.md"):
    with open(output_file, 'w') as f:
        f.write("# Load Test Performance Report\n\n")
        f.write("**Hardware Configuration**: NVIDIA GeForce RTX 3060 (Single GPU)\n\n")
        
        f.write("## Executive Summary\n")
        f.write("Load tests were conducted using `k6` (via Kubernetes Jobs) to verify system stability and performance boundaries.\n")
        f.write("The results below cover Requests Per Second (RPS), Latency (p95), and Resource Utilization.\n\n")

        for sweep_type in ['short', 'long']:
            sweep_results = [r for r in results if r['type'] == sweep_type]
            if not sweep_results: continue
            
            f.write(f"## {sweep_type.capitalize()} Sweep Results\n")
            f.write(f"| Concurrency | RPS | p95 Latency (s) | Avg GPU Util % | Max Mem (MiB) |\n")
            f.write(f"| :--- | :--- | :--- | :--- | :--- |\n")
            
            for r in sweep_results:
                f.write(f"| {r['concurrency']} | {r['rps']:.2f} | {r['p95_latency']:.4f} | {r['avg_gpu_util']:.1f} | {r['max_mem_used']:.1f} |\n")
            f.write("\n")
            
        f.write("## Production Readiness Guide\n")
        f.write("### 1. Observability\n")
        f.write("- **Metrics**: Deploy `dcgm-exporter` to scrape GPU metrics into Prometheus. Dashboard via Grafana.\n")
        f.write("- **Tracing**: Integrate OpenTelemetry sidecar for request-level tracing (e.g. Jaeger) to pinpoint latency bottlenecks.\n")
        f.write("### 2. Autoscaling\n")
        f.write("- **HPA**: Use Kubernetes HPA with custom metrics (e.g., `avg_gpu_util > 85%` or `requests_per_second`).\n")
        f.write("- **KEDA**: Event-driven autoscaling based on queue depth (e.g. Kafka/RabbitMQ) if using async inference.\n")
        f.write("### 3. Traffic Management\n")
        f.write("- **Ingress**: Nginx Ingress Controller (current) is suitable. For advanced routing (canary/blue-green), consider Gateway API + Istio.\n")
        f.write("### 4. Load Testing\n")
        f.write("- **Tools**: `hey` is good for quick baselines. For realistic scenarios, use `Locust` (Python) or `k6` (JS) to simulate user sessions and variable wait times.\n")

if __name__ == "__main__":
    args = parse_args()
    combined_results = []
    
    # Short
    if os.path.exists(args.k6_dir):
        # Determine strict pattern for GPU based on sweep type
        # Assuming filename format: payload_*.csv in gpu_dir
        res = analyze_sweep('short', args.k6_dir, args.gpu_dir, 'short_*.csv')
        if res:
            for r in res: r['type'] = 'short'
            combined_results.extend(res)
            
        # Long (only if files exist/requested, usually mixed in same dir)
        # Check if any long logs exist contextually or just try
        res = analyze_sweep('long', args.k6_dir, args.gpu_dir, 'long_*.csv')
        if res:
             for r in res: r['type'] = 'long'
             combined_results.extend(res)

    if combined_results:
        generate_report(combined_results, args.output)
        print(f"Report generated at {args.output}")

