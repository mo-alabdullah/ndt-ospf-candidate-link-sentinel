#!/usr/bin/env bash
set -euo pipefail
R1=clab-ospf-smoke-r1
R3=clab-ospf-smoke-r3
docker exec "$R1" vtysh -c "configure terminal" -c "interface eth2" \
  -c "ip ospf cost 30" -c "end"
docker exec "$R3" vtysh -c "configure terminal" -c "interface eth1" \
  -c "ip ospf cost 30" -c "end"
sleep 3
echo "Costs restored."
