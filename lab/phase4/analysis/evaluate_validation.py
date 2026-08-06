from __future__ import annotations

import json
from pathlib import Path

from common import evaluate_schedule, load_rows

phase4_dir = Path(__file__).resolve().parents[1]
project_root = phase4_dir.parents[1]
dataset = project_root / "processed-data" / "phase4_dataset.csv"
results_dir = phase4_dir / "results"
results_dir.mkdir(parents=True, exist_ok=True)

rows = load_rows(dataset)
calibration = [
    row for row in rows
    if row["role"] == "calibration"
]
validation = [
    row for row in rows
    if row["role"] == "validation"
]

if not calibration or not validation:
    raise SystemExit(
        "Calibration and validation samples are both required."
    )

calibration_residuals = [
    row["rtt_residual_ms"] for row in calibration
]

schedules = sorted({row["schedule"] for row in validation})
report: dict = {
    "calibration_samples": len(calibration),
    "validation_samples": len(validation),
    "schedules": {},
}

windows = [10, 20, 50]

for schedule in schedules:
    schedule_rows = sorted(
        [
            row for row in validation
            if row["schedule"] == schedule
        ],
        key=lambda row: row["position"],
    )
    report["schedules"][schedule] = evaluate_schedule(
        schedule_rows,
        calibration_residuals,
        windows,
    )

# Choose a rolling window using validation data only:
# 1) fewest unsafe deployments, 2) highest safe acceptance,
# 3) highest overall acceptance, 4) smaller window.
candidates = []
for window in windows:
    name = f"rolling_window_{window}_full_feedback"
    aggregate = {
        "window": window,
        "unsafe_deployments": 0,
        "safe_accepted": 0,
        "accepted": 0,
        "samples": 0,
    }
    for schedule_results in report["schedules"].values():
        result = next(
            item for item in schedule_results
            if item["policy"] == name
        )
        for key in (
            "unsafe_deployments",
            "safe_accepted",
            "accepted",
            "samples",
        ):
            aggregate[key] += result[key]
    candidates.append(aggregate)

selected = sorted(
    candidates,
    key=lambda item: (
        item["unsafe_deployments"],
        -item["safe_accepted"],
        -item["accepted"],
        item["window"],
    ),
)[0]

report["rolling_window_candidates"] = candidates
report["selected_window"] = selected["window"]
report["limitation"] = (
    "Rolling policies use offline full feedback, including outcomes for "
    "changes they would have rejected."
)

(results_dir / "validation_results.json").write_text(
    json.dumps(report, indent=2) + "\n",
    encoding="utf-8",
)
(results_dir / "selected_policy.json").write_text(
    json.dumps(
        {
            "policy": (
                f"rolling_window_{selected['window']}_full_feedback"
            ),
            "rolling_window": selected["window"],
            "selected_using": "validation schedules only",
            "holdout_seen": False,
        },
        indent=2,
    )
    + "\n",
    encoding="utf-8",
)

print(json.dumps(report, indent=2))
