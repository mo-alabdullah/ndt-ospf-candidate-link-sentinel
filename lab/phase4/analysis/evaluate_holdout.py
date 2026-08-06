from __future__ import annotations

import json
from pathlib import Path

from common import evaluate_schedule, load_rows

phase4_dir = Path(__file__).resolve().parents[1]
project_root = phase4_dir.parents[1]
dataset = project_root / "processed-data" / "phase4_dataset.csv"
results_dir = phase4_dir / "results"
selected_path = results_dir / "selected_policy.json"

selected = json.loads(selected_path.read_text(encoding="utf-8"))
window = int(selected["rolling_window"])

rows = load_rows(dataset)
calibration = [
    row for row in rows
    if row["role"] == "calibration"
]
holdout = sorted(
    [
        row for row in rows
        if row["role"] == "holdout"
    ],
    key=lambda row: row["position"],
)

if not calibration or not holdout:
    raise SystemExit(
        "Calibration and holdout samples are both required."
    )

calibration_residuals = [
    row["rtt_residual_ms"] for row in calibration
]

results = evaluate_schedule(
    holdout,
    calibration_residuals,
    [window],
)

report = {
    "holdout_samples": len(holdout),
    "selected_policy": selected,
    "results": results,
    "important_note": (
        "The holdout was not used to select the rolling window. "
        "Rolling evaluation still uses offline full feedback."
    ),
}

(results_dir / "holdout_results.json").write_text(
    json.dumps(report, indent=2) + "\n",
    encoding="utf-8",
)
print(json.dumps(report, indent=2))
