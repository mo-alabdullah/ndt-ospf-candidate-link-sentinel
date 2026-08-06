#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
command -v docker >/dev/null || { echo "Docker is missing." >&2; exit 1; }
command -v containerlab >/dev/null || { echo "containerlab is missing." >&2; exit 1; }
sudo containerlab deploy -t smoke.clab.yml
echo "Run ./scripts/verify.sh"
