#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
for topology in ops.clab.yml twin.clab.yml; do
  sudo containerlab destroy -t "$topology" --cleanup >/dev/null 2>&1 || true
  sudo containerlab deploy -t "$topology"
done
sleep 4
for side in ops twin; do
  for router in r1 r2 r3; do
    c="clab-ospf-${side}-${router}"
    docker exec "$c" sh -c 'test -e /etc/frr/vtysh.conf || touch /etc/frr/vtysh.conf'
    docker exec "$c" vtysh -f /etc/frr/frr.conf
  done
done
echo "Waiting for OSPF convergence..."
sleep 25
echo "Both labs are deployed."
