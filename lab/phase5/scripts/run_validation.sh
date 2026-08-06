#!/usr/bin/env bash
set -euo pipefail

phase5_dir="$(cd "$(dirname "$0")/.." && pwd)"
phase4_schedules="$phase5_dir/../phase4/schedules/generated"

if [[ ! -f "$phase4_schedules/calibration_seed77.csv" ]]; then
  python3 "$phase5_dir/../phase4/schedules/generate_schedules.py"
fi

"$phase5_dir/scripts/run_schedule.sh" \
  "$phase4_schedules/calibration_seed77.csv"

for schedule in \
  randomized_seed101.csv \
  randomized_seed202.csv \
  randomized_seed303.csv \
  abrupt_shift.csv \
  up_down.csv
do
  "$phase5_dir/scripts/run_schedule.sh" "$phase4_schedules/$schedule"
done

python3 "$phase5_dir/analysis/build_dataset.py"
python3 "$phase5_dir/analysis/evaluate_sentinel.py"
