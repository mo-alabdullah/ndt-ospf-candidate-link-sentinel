#!/usr/bin/env bash
set -euo pipefail

phase3_dir="$(cd "$(dirname "$0")/.." && pwd)"
repetitions="${REPETITIONS:-5}"

# Ordered schedule: low drift first, followed by increasingly severe drift.
# This allows later evaluation of a distribution shift.
delays=(0 1 2 5 10 15 20 25 30 35 40)

for delay in "${delays[@]}"; do
  for repetition in $(seq 1 "$repetitions"); do
    echo
    echo "=== delay=${delay}ms repetition=${repetition}/${repetitions} ==="
    "$phase3_dir/scripts/collect_one.sh" "$delay" "$repetition"
  done
done

"$phase3_dir/scripts/set_ops_delay.sh" 0

python3 "$phase3_dir/analysis/build_dataset.py"
python3 "$phase3_dir/analysis/evaluate_gates.py"

echo
echo "Delay sweep complete."
