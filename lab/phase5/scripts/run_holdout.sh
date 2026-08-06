#!/usr/bin/env bash
        set -euo pipefail

        phase5_dir="$(cd "$(dirname "$0")/.." && pwd)"
        phase4_schedules="$phase5_dir/../phase4/schedules/generated"
        frozen="$phase5_dir/results/frozen_policy.json"
        completed="$phase5_dir/results/holdout_results.json"

        if [[ -f "$completed" ]]; then
          echo "Holdout results already exist. Refusing a second evaluation."
          exit 1
        fi

        if [[ ! -f "$frozen" ]]; then
          echo "Missing frozen policy: $frozen" >&2
          exit 1
        fi

        status="$(
          python3 - "$frozen" <<'PY'
import json
import sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
valid = (
    data.get("status") == "frozen_for_holdout"
    and data.get("holdout_seen") is False
    and data.get("parameters_must_not_change_after_holdout") is True
)
print("valid" if valid else "invalid")
PY
        )"

        if [[ "$status" != "valid" ]]; then
          echo "Frozen policy manifest is invalid." >&2
          exit 1
        fi

        if [[ ! -f "$phase4_schedules/holdout_seed909.csv" ]]; then
          python3 \
            "$phase5_dir/../phase4/schedules/generate_schedules.py"
        fi

        "$phase5_dir/scripts/run_schedule.sh" \
          "$phase4_schedules/holdout_seed909.csv"

        python3 "$phase5_dir/analysis/build_holdout_dataset.py"
        python3 "$phase5_dir/analysis/evaluate_holdout.py"
