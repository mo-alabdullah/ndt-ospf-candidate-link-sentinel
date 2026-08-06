#!/usr/bin/env bash
set -euo pipefail

phase4_dir="$(cd "$(dirname "$0")/.." && pwd)"
generated="$phase4_dir/schedules/generated"

python3 "$phase4_dir/schedules/generate_schedules.py"

"$phase4_dir/scripts/run_schedule.sh" "$generated/calibration_seed77.csv"

for schedule in \
  randomized_seed101.csv \
  randomized_seed202.csv \
  randomized_seed303.csv \
  abrupt_shift.csv \
  up_down.csv
do
  "$phase4_dir/scripts/run_schedule.sh" "$generated/$schedule"
done

python3 "$phase4_dir/analysis/build_dataset.py"
python3 "$phase4_dir/analysis/evaluate_validation.py"
