#!/bin/bash
set -e

# Directory setup
mkdir -p loadtest/logs/k6 loadtest/logs/gpu
rm -rf loadtest/logs/k6/* loadtest/logs/gpu/*

CONCURRENCIES=(1 2 4 8 12 16)
# For testing validity, we can reduce C or N, but let's do full.
PAYLOADS=("short" "long")
ITERATIONS=192

# Ensure ConfigMap is up to date
kubectl apply -f loadtest/k6_job.yaml

for payload in "${PAYLOADS[@]}"; do
  echo "Starting ${payload} sweep..."
  
  for c in "${CONCURRENCIES[@]}"; do
    echo "Running ${payload} c=${c}..."
    LOG_FILE="loadtest/logs/k6/${payload}_c${c}_summary.json"
    
    if [ -f "$LOG_FILE" ] && [ -s "$LOG_FILE" ]; then
      echo "Skipping ${payload} c=${c} (Exists)"
      continue
    fi

    JOB_NAME="k6-run-${payload}-c${c}"
    
    # Start GPU logging locally (monitoring the node)
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    GPU_LOG="loadtest/logs/gpu/${payload}_c${c}_${TIMESTAMP}.csv"
    nvidia-smi --query-gpu=timestamp,utilization.gpu,utilization.memory,memory.used,memory.total,temperature.gpu,power.draw \
      --format=csv -l 1 > "$GPU_LOG" &
    PID_GPU=$!
    
    # Clean up previous job if exists
    kubectl delete job $JOB_NAME --ignore-not-found=true
    
    # Generate and Apply Job
    cat loadtest/k6_job.yaml | sed -n '/^apiVersion: batch\/v1/,$p' | \
      sed "s/name: k6-run-temp/name: $JOB_NAME/" | \
      sed "s/value: \"REPLACE_VUS\"/value: \"$c\"/" | \
      sed "s/value: \"REPLACE_N\"/value: \"$ITERATIONS\"/" | \
      sed "s/value: \"REPLACE_PAYLOAD\"/value: \"$payload\"/" | \
      kubectl apply -f -
      
    # Wait for completion
    echo "Waiting for job $JOB_NAME..."
    kubectl wait --for=condition=complete job/$JOB_NAME --timeout=900s
    
    # Capture Logs (stdout containing JSON summary)
    kubectl logs job/$JOB_NAME > "loadtest/logs/k6/${payload}_c${c}_summary.json"
    
    # Stop GPU logging
    kill $PID_GPU || true
    
    echo "Completed ${payload} c=${c}"
    sleep 5
  done
done

echo "K8s Sweep Complete."
