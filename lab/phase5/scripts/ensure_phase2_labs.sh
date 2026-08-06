#!/usr/bin/env bash
set -euo pipefail

phase5_dir="$(cd "$(dirname "$0")/.." && pwd)"
phase2_dir="$(cd "$phase5_dir/../phase2" && pwd)"

required=(
  clab-ospf-ops-r1
  clab-ospf-ops-r3
  clab-ospf-ops-h1
  clab-ospf-twin-r1
  clab-ospf-twin-r3
  clab-ospf-twin-h1
)

missing=0
for container in "${required[@]}"; do
  if ! docker inspect "$container" >/dev/null 2>&1; then
    echo "Missing container: $container"
    missing=1
  fi
done

if [[ "$missing" -eq 1 ]]; then
  chmod +x "$phase2_dir"/scripts/*.sh
  "$phase2_dir/scripts/deploy_both.sh"
fi

chmod +x "$phase2_dir"/scripts/*.sh
"$phase2_dir/scripts/verify_both.sh"
