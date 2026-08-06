from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from statistics import mean

script_dir = Path(__file__).resolve().parent
project_root = script_dir.parents[2]
dataset_path = project_root / "processed-data" / "phase3_delay_sweep.csv"
output_path = project_root / "results" / "phase3_gate_summary.json"
output_path.parent.mkdir(parents=True, exist_ok=True)

SLA_MS = 50.0
FIXED_MARGIN_MS = 10.0
QUANTILE_LEVEL = 0.95
CALIBRATION_FRACTION = 0.40
ROLLING_WINDOW = 20

def quantile_higher(values: list[float], level: float) -> float:
    if not values:
        raise ValueError("Quantile requires at least one value.")
    ordered = sorted(values)
    index = max(
        0,
        min(len(ordered) - 1, math.ceil(level * len(ordered)) - 1),
    )
    return ordered[index]

with dataset_path.open(encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))

for row in rows:
    for key in (
        "ops_rtt_avg_ms",
        "twin_rtt_avg_ms",
        "rtt_residual_ms",
        "per_direction_delay_ms",
    ):
        row[key] = float(row[key])
    row["unsafe"] = row["operational_unsafe_latency"].lower() == "true"

split = max(1, int(len(rows) * CALIBRATION_FRACTION))
calibration = rows[:split]
test = rows[split:]

static_margin = quantile_higher(
    [row["rtt_residual_ms"] for row in calibration],
    QUANTILE_LEVEL,
)

def summarize(name: str, decisions: list[tuple[bool, bool]]) -> dict:
    accepted = [unsafe for deploy, unsafe in decisions if deploy]
    rejected = [unsafe for deploy, unsafe in decisions if not deploy]
    unsafe_accepted = sum(1 for unsafe in accepted if unsafe)
    safe_accepted = sum(1 for unsafe in accepted if not unsafe)
    safe_rejected = sum(1 for unsafe in rejected if not unsafe)

    return {
        "policy": name,
        "test_samples": len(decisions),
        "accepted": len(accepted),
        "acceptance_rate": len(accepted) / len(decisions),
        "unsafe_deployments": unsafe_accepted,
        "unsafe_deployment_rate_among_accepted": (
            unsafe_accepted / len(accepted) if accepted else 0.0
        ),
        "safe_accepted": safe_accepted,
        "safe_rejected": safe_rejected,
    }

results = []

results.append(
    summarize(
        "direct",
        [(True, row["unsafe"]) for row in test],
    )
)

results.append(
    summarize(
        "twin_only",
        [
            (row["twin_rtt_avg_ms"] <= SLA_MS, row["unsafe"])
            for row in test
        ],
    )
)

results.append(
    summarize(
        "fixed_margin_10ms",
        [
            (
                row["twin_rtt_avg_ms"] + FIXED_MARGIN_MS <= SLA_MS,
                row["unsafe"],
            )
            for row in test
        ],
    )
)

results.append(
    summarize(
        "static_residual_quantile",
        [
            (
                row["twin_rtt_avg_ms"] + static_margin <= SLA_MS,
                row["unsafe"],
            )
            for row in test
        ],
    )
)

history = [row["rtt_residual_ms"] for row in calibration]
rolling_decisions: list[tuple[bool, bool]] = []
rolling_margins: list[float] = []

# Offline full-feedback replay: every realized residual is appended after
# the decision. This is a baseline, not yet a selective-feedback solution.
for row in test:
    margin = quantile_higher(
        history[-ROLLING_WINDOW:],
        QUANTILE_LEVEL,
    )
    deploy = row["twin_rtt_avg_ms"] + margin <= SLA_MS
    rolling_decisions.append((deploy, row["unsafe"]))
    rolling_margins.append(margin)
    history.append(row["rtt_residual_ms"])

rolling_result = summarize(
    "rolling_residual_quantile_full_feedback",
    rolling_decisions,
)
rolling_result["mean_margin_ms"] = mean(rolling_margins)
results.append(rolling_result)

report = {
    "dataset": str(dataset_path),
    "total_samples": len(rows),
    "calibration_samples": len(calibration),
    "test_samples": len(test),
    "latency_sla_ms": SLA_MS,
    "static_quantile_level": QUANTILE_LEVEL,
    "static_margin_ms": static_margin,
    "rolling_window": ROLLING_WINDOW,
    "important_note": (
        "Rolling evaluation uses offline full feedback. It does not solve "
        "the selective-feedback problem for rejected changes."
    ),
    "policies": results,
}

output_path.write_text(
    json.dumps(report, indent=2) + "\n",
    encoding="utf-8",
)
print(json.dumps(report, indent=2))
print(f"Wrote {output_path}")
