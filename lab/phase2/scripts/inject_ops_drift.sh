#!/usr/bin/env bash
set -euo pipefail
docker exec clab-ospf-ops-r1 tc qdisc replace dev eth2 root netem delay 30ms
docker exec clab-ospf-ops-r3 tc qdisc replace dev eth1 root netem delay 30ms
echo "Operational-only direct-link drift injected: approximately 60 ms RTT."
