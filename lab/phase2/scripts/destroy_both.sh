#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
sudo containerlab destroy -t ops.clab.yml --cleanup || true
sudo containerlab destroy -t twin.clab.yml --cleanup || true
