#!/usr/bin/env bash
set -euo pipefail

for side in ops twin; do
  echo "===== $side ====="
  r1="clab-ospf-${side}-r1"
  h1="clab-ospf-${side}-h1"

  neighbors="$(docker exec "$r1" vtysh -c "show ip ospf neighbor")"
  echo "$neighbors"

  full_count="$(printf '%s\n' "$neighbors" | grep -c 'Full/-' || true)"
  if [ "$full_count" -ne 2 ]; then
    echo "ERROR: $side r1 does not have two Full OSPF neighbors." >&2
    exit 1
  fi

  route="$(docker exec "$r1" vtysh -c "show ip route 192.168.13.0/24")"
  echo "$route"
  printf '%s\n' "$route" | grep -q 'Known via "ospf"' || {
    echo "ERROR: $side target route is not installed through OSPF." >&2
    exit 1
  }

  ping_output="$(docker exec "$h1" ping -c 10 -i 0.1 -W 2 192.168.13.2)"
  echo "$ping_output"
  printf '%s\n' "$ping_output" | grep -q '0% packet loss' || {
    echo "ERROR: $side baseline ping is not loss-free." >&2
    exit 1
  }
done

echo "PASS: both operational and twin labs are converged and reachable."
