from __future__ import annotations

import json
from pathlib import Path
import sys

if len(sys.argv) != 4:
    raise SystemExit(
        "Usage: annotate_summary.py <summary.json> <delay-ms> <repetition>"
    )

path = Path(sys.argv[1])
delay_ms = float(sys.argv[2])
repetition = int(sys.argv[3])

data = json.loads(path.read_text(encoding="utf-8"))
data["scenario"] = {
    "type": "hidden_direct_link_delay",
    "per_direction_delay_ms": delay_ms,
    "repetition": repetition,
    "candidate_direct_link_cost": 5,
    "latency_sla_ms": 50.0,
}
data["labels"] = {
    "operational_unsafe_latency": (
        data["operational"]["rtt_avg_ms"] > 50.0
    ),
    "twin_predicted_safe_latency": (
        data["twin"]["rtt_avg_ms"] <= 50.0
    ),
}

path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
