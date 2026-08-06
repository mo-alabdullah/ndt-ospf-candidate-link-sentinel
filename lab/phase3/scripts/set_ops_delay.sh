#!/usr/bin/env bash
set -euo pipefail

delay_ms="${1:?Usage: set_ops_delay.sh <per-direction-delay-ms>}"

if ! [[ "$delay_ms" =~ ^[0-9]+([.][0-9]+)?$ ]]; then
  echo "Delay must be a non-negative number." >&2
  exit 1
fi

r1="clab-ospf-ops-r1"
r3="clab-ospf-ops-r3"

if [[ "$delay_ms" == "0" || "$delay_ms" == "0.0" ]]; then
  docker exec "$r1" tc qdisc del dev eth2 root 2>/dev/null || true
  docker exec "$r3" tc qdisc del dev eth1 root 2>/dev/null || true
  echo "Operational direct-link delay removed."
else
  docker exec "$r1" tc qdisc replace dev eth2 root netem delay "${delay_ms}ms"
  docker exec "$r3" tc qdisc replace dev eth1 root netem delay "${delay_ms}ms"
  echo "Operational direct-link delay set to ${delay_ms} ms per direction."
fi
