#!/usr/bin/env bash
set -euo pipefail
LAB=ospf-smoke
R1="clab-${LAB}-r1"; R2="clab-${LAB}-r2"; R3="clab-${LAB}-r3"
H1="clab-${LAB}-h1"; H3="clab-${LAB}-h3"
for c in "$R1" "$R2" "$R3" "$H1" "$H3"; do
  docker inspect "$c" >/dev/null 2>&1 || { echo "$c is not running." >&2; exit 1; }
done
for r in "$R1" "$R2" "$R3"; do
  echo "=== $r neighbors ==="
  docker exec "$r" vtysh -c "show ip ospf neighbor"
done
echo "=== r1 route toward h3 LAN ==="
docker exec "$R1" vtysh -c "show ip route 192.168.13.0/24"
echo "=== h1 to h3 ping ==="
docker exec "$H1" ping -c 4 -W 2 192.168.13.2
echo "PASS"
