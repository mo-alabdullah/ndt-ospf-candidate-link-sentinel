#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
sudo containerlab destroy -t smoke.clab.yml --cleanup
