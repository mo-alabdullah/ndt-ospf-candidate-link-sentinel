from __future__ import annotations

import csv
import json
from pathlib import Path
import re

script_dir = Path(__file__).resolve().parent
project_root = script_dir.parents[2]
raw_root = project_root / "raw-data" / "phase2"
output = project_root / "processed-data" / "phase3_delay_sweep.csv"
output.parent.mkdir(parents=True, exist_ok=True)

rows: list[dict] = []

for summary_path in sorted(raw_root.glob("*-delay-*ms-rep-*/summary.json")):
    data = json.loads(summary_path.read_text(encoding="utf-8"))
    scenario = data.get("scenario", {})
    labels = data.get("labels", {})

    rows.append(
        {
            "sample_id": summary_path.parent.name,
            "per_direction_delay_ms": scenario["per_direction_delay_ms"],
            "repetition": scenario["repetition"],
            "ops_rtt_avg_ms": data["operational"]["rtt_avg_ms"],
            "twin_rtt_avg_ms": data["twin"]["rtt_avg_ms"],
            "rtt_residual_ms": data["residuals"]["rtt_avg_ms"],
            "ops_packet_loss_percent": (
                data["operational"]["packet_loss_percent"]
            ),
            "twin_packet_loss_percent": (
                data["twin"]["packet_loss_percent"]
            ),
            "operational_unsafe_latency": (
                labels["operational_unsafe_latency"]
            ),
            "twin_predicted_safe_latency": (
                labels["twin_predicted_safe_latency"]
            ),
        }
    )

if not rows:
    raise SystemExit(f"No annotated summaries found under {raw_root}")

fieldnames = list(rows[0])
with output.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"Wrote {len(rows)} rows to {output}")
