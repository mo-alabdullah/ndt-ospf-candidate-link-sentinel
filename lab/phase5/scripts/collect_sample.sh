#!/usr/bin/env bash
set -euo pipefail

schedule="${1:?Usage: collect_sample.sh <schedule> <position> <delay-ms> <repetition> <role> <seed>}"
position="${2:?}"
delay_ms="${3:?}"
repetition="${4:?}"
role="${5:?}"
seed="${6:-}"

role="${role%$'\r'}"
seed="${seed%$'\r'}"

phase5_dir="$(cd "$(dirname "$0")/.." && pwd)"
project_root="$(cd "$phase5_dir/../.." && pwd)"
raw_root="$project_root/raw-data/phase5"
sample_id="${schedule}-pos-$(printf '%03d' "$position")-delay-${delay_ms}ms-rep-${repetition}"
out="$raw_root/$sample_id"

mkdir -p "$out"

"$phase5_dir/scripts/set_ops_delay.sh" "$delay_ms"
"$phase5_dir/scripts/set_candidate_state.sh" baseline

# Pre-deployment candidate-link probes. The destination is directly
# connected, so the probe traverses r1-r3 even while OSPF still prefers r2.
docker exec clab-ospf-ops-r1 \
  ping -c 20 -i 0.1 -W 2 192.168.2.2 \
  > "$out/ops-link-probe.txt"

docker exec clab-ospf-twin-r1 \
  ping -c 20 -i 0.1 -W 2 192.168.2.2 \
  > "$out/twin-link-probe.txt"

# Apply the candidate to observe its realized end-to-end outcome.
"$phase5_dir/scripts/set_candidate_state.sh" candidate

for side in ops twin; do
  r1="clab-ospf-${side}-r1"
  h1="clab-ospf-${side}-h1"

  docker exec "$r1" vtysh -c "show ip route 192.168.13.0/24" \
    > "$out/${side}-route.txt"

  docker exec "$h1" ping -c 20 -i 0.1 -W 2 192.168.13.2 \
    > "$out/${side}-e2e-ping.txt"
done

python3 "$phase5_dir/analysis/parse_sample.py" \
  "$out" \
  "$schedule" \
  "$position" \
  "$delay_ms" \
  "$repetition" \
  "$role" \
  "$seed"

echo "Collected $sample_id"
