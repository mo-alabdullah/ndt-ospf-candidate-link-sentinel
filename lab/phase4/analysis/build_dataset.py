from __future__ import annotations

import csv
import json
from pathlib import Path

phase4_dir = Path(__file__).resolve().parents[1]
project_root = phase4_dir.parents[1]
raw_root = project_root / "raw-data" / "phase4"
output = project_root / "processed-data" / "phase4_dataset.csv"
output.parent.mkdir(parents=True, exist_ok=True)

rows: list[dict] = []

for summary_path in sorted(raw_root.glob("*/summary.json")):
    data = json.loads(summary_path.read_text(encoding="utf-8"))
    rows.append(
        {
            "sample_id": data["sample_id"],
            "schedule": data["schedule"],
            "position": data["position"],
            "delay_ms": data["delay_ms"],
            "repetition": data["repetition"],
            "role": data["role"],
            "seed": "" if data["seed"] is None else data["seed"],
            "ops_rtt_avg_ms": data["operational"]["rtt_avg_ms"],
            "twin_rtt_avg_ms": data["twin"]["rtt_avg_ms"],
            "rtt_residual_ms": data["residuals"]["rtt_avg_ms"],
            "ops_packet_loss_percent": (
                data["operational"]["packet_loss_percent"]
            ),
            "twin_packet_loss_percent": (
                data["twin"]["packet_loss_percent"]
            ),
            "ops_route_metric": data["operational"]["route"]["metric"],
            "twin_route_metric": data["twin"]["route"]["metric"],
            "ops_next_hop": data["operational"]["route"]["next_hop"],
            "twin_next_hop": data["twin"]["route"]["next_hop"],
            "route_match": data["labels"]["route_match"],
            "operational_unsafe_latency": (
                data["labels"]["operational_unsafe_latency"]
            ),
            "twin_predicted_safe_latency": (
                data["labels"]["twin_predicted_safe_latency"]
            ),
        }
    )

if not rows:
    raise SystemExit(f"No Phase 4 summaries found under {raw_root}")

with output.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)

print(f"Wrote {len(rows)} rows to {output}")
