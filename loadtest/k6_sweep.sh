#!/bin/bash
set -e

# Directory setup
mkdir -p loadtest/logs/k6 loadtest/logs/gpu
rm -rf loadtest/logs/k6/* loadtest/logs/gpu/*

CONCURRENCIES=(1 2 4 8 12 16)
PAYLOADS=("short" "long")
ITERATIONS=192 # Divisible by all concurrencies

for payload in "${PAYLOADS[@]}"; do
  echo "Starting ${payload} sweep..."
  
  for c in "${CONCURRENCIES[@]}"; do
    echo "Running ${payload} c=${c}..."
    
    # Start GPU logging
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    GPU_LOG="loadtest/logs/gpu/${payload}_c${c}_${TIMESTAMP}.csv"
    nvidia-smi --query-gpu=timestamp,utilization.gpu,utilization.memory,memory.used,memory.total,temperature.gpu,power.draw \
      --format=csv -l 1 > "$GPU_LOG" &
    PID_GPU=$!
    
    # Run k6
    # We use ./k6 assumption (in current dir)
    ./k6 run -e VUS=${c} -e TOTAL_N=${ITERATIONS} -e PAYLOAD_TYPE=${payload} loadtest/k6_load_test.js \
      --summary-export "loadtest/logs/k6/${payload}_c${c}_summary.json" > "loadtest/logs/k6/${payload}_c${c}.log" 2>&1
    
    # Stop GPU logging
    kill $PID_GPU
    
    echo "Completed ${payload} c=${c}"
    sleep 5
  done
done

echo "Sweep Complete."
