#!/usr/bin/env bash
set -euo pipefail
for side in ops twin; do
  r1="clab-ospf-${side}-r1"; r3="clab-ospf-${side}-r3"
  docker exec "$r1" vtysh -c "configure terminal" -c "interface eth2" -c "ip ospf cost 30" -c "end"
  docker exec "$r3" vtysh -c "configure terminal" -c "interface eth1" -c "ip ospf cost 30" -c "end"
done
docker exec clab-ospf-ops-r1 tc qdisc del dev eth2 root 2>/dev/null || true
docker exec clab-ospf-ops-r3 tc qdisc del dev eth1 root 2>/dev/null || true
sleep 5
echo "Experiment state reset."
