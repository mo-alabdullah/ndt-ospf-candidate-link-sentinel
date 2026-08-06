#!/usr/bin/env bash
set -euo pipefail
for side in ops twin; do
  r1="clab-ospf-${side}-r1"; r3="clab-ospf-${side}-r3"
  docker exec "$r1" vtysh -c "configure terminal" -c "interface eth2" -c "ip ospf cost 5" -c "end"
  docker exec "$r3" vtysh -c "configure terminal" -c "interface eth1" -c "ip ospf cost 5" -c "end"
done
sleep 5
echo "Candidate cost change applied to operational network and twin."
