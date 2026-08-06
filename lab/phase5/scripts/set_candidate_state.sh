#!/usr/bin/env bash
set -euo pipefail

state="${1:?Usage: set_candidate_state.sh <baseline|candidate>}"

case "$state" in
  baseline) cost=30 ;;
  candidate) cost=5 ;;
  *)
    echo "State must be baseline or candidate." >&2
    exit 1
    ;;
esac

for side in ops twin; do
  r1="clab-ospf-${side}-r1"
  r3="clab-ospf-${side}-r3"

  docker exec "$r1" vtysh \
    -c "configure terminal" \
    -c "interface eth2" \
    -c "ip ospf cost $cost" \
    -c "end"

  docker exec "$r3" vtysh \
    -c "configure terminal" \
    -c "interface eth1" \
    -c "ip ospf cost $cost" \
    -c "end"
done

sleep 2
