#!/usr/bin/env bash
set -euo pipefail

delay_ms="${1:?Usage: collect_one.sh <delay-ms> <repetition>}"
repetition="${2:?Usage: collect_one.sh <delay-ms> <repetition>}"

phase2_dir="$(cd "$(dirname "$0")/../../phase2" && pwd)"
phase3_dir="$(cd "$(dirname "$0")/.." && pwd)"
project_root="$(cd "$phase3_dir/../.." && pwd)"

"$phase3_dir/scripts/set_ops_delay.sh" "$delay_ms"
"$phase3_dir/scripts/ensure_candidate_route.sh"

label="delay-${delay_ms}ms-rep-${repetition}"
"$phase2_dir/scripts/measure_pair.sh" "$label"

latest_dir="$(
  find "$project_root/raw-data/phase2" -maxdepth 1 -type d \
    -name "*-${label}" -print | sort | tail -n 1
)"

if [[ -z "$latest_dir" ]]; then
  echo "Could not locate output directory for $label." >&2
  exit 1
fi

python3 "$phase3_dir/scripts/annotate_summary.py" \
  "$latest_dir/summary.json" "$delay_ms" "$repetition"

echo "Collected $label"
