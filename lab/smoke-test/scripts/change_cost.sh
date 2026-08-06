#!/usr/bin/env bash
set -euo pipefail
R1=clab-ospf-smoke-r1
R3=clab-ospf-smoke-r3
docker exec "$R1" vtysh -c "configure terminal" -c "interface eth2" \
  -c "ip ospf cost 5" -c "end"
docker exec "$R3" vtysh -c "configure terminal" -c "interface eth1" \
  -c "ip ospf cost 5" -c "end"
sleep 3
docker exec "$R1" vtysh -c "show ip route 192.168.13.0/24"
