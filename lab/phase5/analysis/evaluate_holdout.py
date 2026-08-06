from __future__ import annotations

import csv
import json
from pathlib import Path

phase5_dir = Path(__file__).resolve().parents[1]
project_root = phase5_dir.parents[1]
results_dir = phase5_dir / "results"
policy_path = results_dir / "frozen_policy.json"
dataset_path = (
    project_root
    / "processed-data"
    / "phase5_holdout_dataset.csv"
)

policy = json.loads(
    policy_path.read_text(encoding="utf-8")
)

if policy.get("status") != "frozen_for_holdout":
    raise SystemExit("Policy is not frozen for holdout.")
if policy.get("holdout_seen") is not False:
    raise SystemExit("Holdout is already marked as seen.")

with dataset_path.open(encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))

if len(rows) != 33:
    raise SystemExit(
        f"Expected 33 holdout rows, found {len(rows)}."
    )

margin = float(policy["conformal_margin_ms"])
sla = float(policy["latency_sla_ms"])

results = {
    "samples": len(rows),
    "accepted": 0,
    "unsafe_deployments": 0,
    "safe_accepted": 0,
    "safe_rejected": 0,
}

records = []

for row in rows:
    prediction = float(row["corrected_prediction_ms"])
    observed = float(row["ops_e2e_rtt_avg_ms"])
    deploy = prediction + margin <= sla
    unsafe = observed > sla

    results["accepted"] += int(deploy)
    results["unsafe_deployments"] += int(
        deploy and unsafe
    )
    results["safe_accepted"] += int(
        deploy and not unsafe
    )
    results["safe_rejected"] += int(
        not deploy and not unsafe
    )

    records.append(
        {
            "sample_id": row["sample_id"],
            "corrected_prediction_ms": prediction,
            "conformal_upper_bound_ms": (
                prediction + margin
            ),
            "observed_rtt_ms": observed,
            "deploy": deploy,
            "unsafe": unsafe,
        }
    )

safe_total = (
    results["safe_accepted"]
    + results["safe_rejected"]
)
results["acceptance_rate"] = (
    results["accepted"] / results["samples"]
)
results["unsafe_rate_among_accepted"] = (
    results["unsafe_deployments"]
    / results["accepted"]
    if results["accepted"]
    else None
)
results["safe_coverage"] = (
    results["safe_accepted"] / safe_total
    if safe_total
    else 0.0
)

report = {
    "evaluation": "untouched_holdout",
    "policy": policy,
    "results": results,
    "records": records,
    "parameters_changed_after_freeze": False,
}

output = results_dir / "holdout_results.json"
output.write_text(
    json.dumps(report, indent=2) + "\n",
    encoding="utf-8",
)

print(json.dumps(results, indent=2))
