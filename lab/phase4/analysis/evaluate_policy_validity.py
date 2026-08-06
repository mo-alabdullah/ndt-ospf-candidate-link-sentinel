from __future__ import annotations

import json
from pathlib import Path

phase4_dir = Path(__file__).resolve().parents[1]
results_dir = phase4_dir / "results"
validation_path = results_dir / "validation_results.json"
output_path = results_dir / "policy_decision.json"

validation = json.loads(
    validation_path.read_text(encoding="utf-8")
)

aggregate: dict[str, dict] = {}

for schedule, results in validation["schedules"].items():
    for result in results:
        policy = result["policy"]
        item = aggregate.setdefault(
            policy,
            {
                "policy": policy,
                "samples": 0,
                "accepted": 0,
                "unsafe_deployments": 0,
                "safe_accepted": 0,
                "safe_rejected": 0,
                "schedules_with_safe_acceptance": 0,
                "schedule_count": 0,
            },
        )
        item["samples"] += result["samples"]
        item["accepted"] += result["accepted"]
        item["unsafe_deployments"] += (
            result["unsafe_deployments"]
        )
        item["safe_accepted"] += result["safe_accepted"]
        item["safe_rejected"] += result["safe_rejected"]
        item["schedule_count"] += 1
        if result["safe_accepted"] > 0:
            item["schedules_with_safe_acceptance"] += 1

for item in aggregate.values():
    safe_total = item["safe_accepted"] + item["safe_rejected"]
    item["acceptance_rate"] = (
        item["accepted"] / item["samples"]
        if item["samples"]
        else 0.0
    )
    item["unsafe_rate_among_accepted"] = (
        item["unsafe_deployments"] / item["accepted"]
        if item["accepted"]
        else None
    )
    item["safe_coverage"] = (
        item["safe_accepted"] / safe_total
        if safe_total
        else 0.0
    )
    item["non_vacuous"] = (
        item["accepted"] > 0
        and item["safe_accepted"] > 0
    )
    item["schedule_robust_utility"] = (
        item["schedules_with_safe_acceptance"]
        == item["schedule_count"]
    )

rolling_names = [
    "rolling_window_10_full_feedback",
    "rolling_window_20_full_feedback",
    "rolling_window_50_full_feedback",
]
candidates = [aggregate[name] for name in rolling_names]

valid = [
    item
    for item in candidates
    if item["non_vacuous"]
    and item["schedule_robust_utility"]
]

if valid:
    selected = sorted(
        valid,
        key=lambda item: (
            item["unsafe_deployments"],
            -item["safe_accepted"],
            -item["accepted"],
        ),
    )[0]
    decision = {
        "status": "policy_ready_for_freeze",
        "holdout_locked": False,
        "selected_policy": selected,
        "holdout_seen": False,
    }
else:
    decision = {
        "status": "method_revision_required",
        "holdout_locked": True,
        "reason": (
            "No tested rolling policy is both non-vacuous and "
            "utility-bearing across every validation schedule."
        ),
        "rolling_candidates": candidates,
        "holdout_seen": False,
    }

output_path.write_text(
    json.dumps(decision, indent=2) + "\n",
    encoding="utf-8",
)
print(json.dumps(decision, indent=2))
