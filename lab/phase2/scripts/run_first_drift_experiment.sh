#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
./scripts/reset_experiment.sh
./scripts/measure_pair.sh baseline
./scripts/inject_ops_drift.sh
./scripts/apply_candidate_both.sh
./scripts/measure_pair.sh drifted-candidate
echo "First twin-to-operational drift experiment completed."
