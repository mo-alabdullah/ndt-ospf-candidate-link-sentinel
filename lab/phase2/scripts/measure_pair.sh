#!/usr/bin/env bash
set -euo pipefail
label="${1:-measurement}"; timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
root="$(cd "$(dirname "$0")/../../.." && pwd)"; out="$root/raw-data/phase2/${timestamp}-${label}"
mkdir -p "$out"
for side in ops twin; do
  r1="clab-ospf-${side}-r1"; h1="clab-ospf-${side}-h1"
  docker exec "$r1" vtysh -c "show ip route 192.168.13.0/24" > "$out/${side}-route.txt"
  docker exec "$h1" ping -c 20 -i 0.1 -W 2 192.168.13.2 > "$out/${side}-ping.txt"
done
python3 "$(dirname "$0")/parse_pair.py" "$out"
echo "Saved experiment evidence to: $out"
