#!/usr/bin/env bash
set -euo pipefail

phase4_dir="$(cd "$(dirname "$0")/.." && pwd)"
generated="$phase4_dir/schedules/generated"
selected="$phase4_dir/results/selected_policy.json"

if [[ ! -f "$selected" ]]; then
  echo "Run validation and select a policy before the holdout." >&2
  exit 1
fi

python3 "$phase4_dir/schedules/generate_schedules.py"
"$phase4_dir/scripts/run_schedule.sh" "$generated/holdout_seed909.csv"

python3 "$phase4_dir/analysis/build_dataset.py"
python3 "$phase4_dir/analysis/evaluate_holdout.py"
