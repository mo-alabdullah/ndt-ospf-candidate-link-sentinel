#!/usr/bin/env bash
set -euo pipefail

schedule_file="${1:?Usage: run_schedule.sh <schedule.csv>}"

phase4_dir="$(cd "$(dirname "$0")/.." && pwd)"
project_root="$(cd "$phase4_dir/../.." && pwd)"
schedule_path="$(python3 -c 'import os,sys; print(os.path.abspath(sys.argv[1]))' "$schedule_file")"

if [[ ! -f "$schedule_path" ]]; then
  echo "Schedule not found: $schedule_path" >&2
  exit 1
fi

"$phase4_dir/scripts/ensure_phase2_labs.sh"

tail -n +2 "$schedule_path" | while IFS=, read -r schedule position delay repetition seed role; do
  # Skip a sample that has already been collected.
  pattern="$project_root/raw-data/phase4/${schedule}-pos-$(printf '%03d' "$position")-delay-${delay}ms-rep-${repetition}/summary.json"
  if [[ -f "$pattern" ]]; then
    echo "Skipping existing sample: $pattern"
    continue
  fi

  "$phase4_dir/scripts/collect_sample.sh" \
    "$schedule" \
    "$position" \
    "$delay" \
    "$repetition" \
    "$role" \
    "$seed"
done

"$phase4_dir/scripts/set_ops_delay.sh" 0
