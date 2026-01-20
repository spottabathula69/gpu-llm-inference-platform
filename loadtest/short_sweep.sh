#!/bin/bash

set -e

# Runn the following command in a seperate window to log the nvidia-smi output to a file:
# mkdir -p loadtest/gpu_logs
# nvidia-smi --query-gpu=timestamp,utilization.gpu,utilization.memory,memory.used,memory.total,temperature.gpu,power.draw \
#   --format=csv -l 1 | tee "loadtest/gpu_logs/short_sweep_$(date +%Y%m%d_%H%M%S).csv"


# n=240 is 48 * 5. Divisible by 1, 2, 4, 8, 12, 16.
# Provides robust stats while keeping runtime manageable.
n=240

for c in 1 2 4 8 12 16; do
  echo "=== SHORT sweep: c=$c, n=$n ==="
  hey -n "$n" -c "$c"  -t 120 -m POST \
    -H "Content-Type: application/json" \
    -D loadtest/chat_short.json \
    http://llm.local/v1/chat/completions \
    > "loadtest/logs/hey/short_c${c}_baseline.txt"
  echo "Completed c=$c"
  sleep 5
done
touch loadtest/logs/hey/short_done.flag
