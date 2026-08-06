from __future__ import annotations

import csv
import json
from pathlib import Path

phase5_dir = Path(__file__).resolve().parents[1]
project_root = phase5_dir.parents[1]
raw_root = project_root / "raw-data" / "phase5"
output = (
    project_root
    / "processed-data"
    / "phase5_holdout_dataset.csv"
)
output.parent.mkdir(parents=True, exist_ok=True)

rows: list[dict] = []

for summary_path in sorted(raw_root.glob("*/summary.json")):
    data = json.loads(
        summary_path.read_text(encoding="utf-8")
    )
    if str(data.get("role", "")).strip() != "holdout":
        continue

    rows.append(
        {
            "sample_id": data["sample_id"],
            "schedule": data["schedule"],
            "position": data["position"],
            "delay_ms": data["delay_ms"],
            "repetition": data["repetition"],
            "role": "holdout",
            "seed": (
                ""
                if data["seed"] is None
                else data["seed"]
            ),
            "ops_link_rtt_avg_ms": (
                data["predeployment_probe"]
                ["operational_link"]["rtt_avg_ms"]
            ),
            "twin_link_rtt_avg_ms": (
                data["predeployment_probe"]
                ["twin_link"]["rtt_avg_ms"]
            ),
            "link_delta_ms": (
                data["predeployment_probe"]["link_delta_ms"]
            ),
            "ops_e2e_rtt_avg_ms": (
                data["candidate_outcome"]
                ["operational_e2e"]["rtt_avg_ms"]
            ),
            "twin_e2e_rtt_avg_ms": (
                data["candidate_outcome"]
                ["twin_e2e"]["rtt_avg_ms"]
            ),
            "corrected_prediction_ms": (
                data["sentinel"]["corrected_prediction_ms"]
            ),
            "corrected_residual_ms": (
                data["sentinel"]["corrected_residual_ms"]
            ),
            "operational_unsafe_latency": (
                data["labels"]
                ["operational_unsafe_latency"]
            ),
            "route_match": data["labels"]["route_match"],
        }
    )

if len(rows) != 33:
    raise SystemExit(
        f"Expected 33 completed holdout samples, found {len(rows)}."
    )

with output.open(
    "w",
    newline="",
    encoding="utf-8",
) as handle:
    writer = csv.DictWriter(
        handle,
        fieldnames=list(rows[0]),
    )
    writer.writeheader()
    writer.writerows(rows)

print(f"Wrote {len(rows)} rows to {output}")
