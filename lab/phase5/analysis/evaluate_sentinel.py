from __future__ import annotations

import csv
import json
import math
from pathlib import Path

SLA_MS = 50.0
ALPHA = 0.05

phase5_dir = Path(__file__).resolve().parents[1]
project_root = phase5_dir.parents[1]
dataset = project_root / "processed-data" / "phase5_sentinel_dataset.csv"
results_dir = phase5_dir / "results"
results_dir.mkdir(parents=True, exist_ok=True)


def load_rows() -> list[dict]:
    with dataset.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    for row in rows:
        for key in (
            "delay_ms",
            "ops_link_rtt_avg_ms",
            "twin_link_rtt_avg_ms",
            "link_delta_ms",
            "ops_e2e_rtt_avg_ms",
            "twin_e2e_rtt_avg_ms",
            "corrected_prediction_ms",
            "corrected_residual_ms",
        ):
            row[key] = float(row[key])

        row["position"] = int(row["position"])
        row["repetition"] = int(row["repetition"])
        row["role"] = row["role"].strip()
        row["schedule"] = row["schedule"].strip()
        row["unsafe"] = (
            row["operational_unsafe_latency"].strip().lower() == "true"
        )

    return rows


def conformal_upper_quantile(
    values: list[float],
    alpha: float,
) -> tuple[float, int]:
    if not values:
        raise ValueError("Calibration residuals are required.")

    ordered = sorted(values)
    rank = math.ceil((len(ordered) + 1) * (1 - alpha))
    rank = min(max(rank, 1), len(ordered))
    return ordered[rank - 1], rank


def summarize(
    name: str,
    decisions: list[tuple[bool, bool]],
) -> dict:
    accepted = [
        unsafe for deploy, unsafe in decisions if deploy
    ]
    rejected = [
        unsafe for deploy, unsafe in decisions if not deploy
    ]

    unsafe_accepted = sum(accepted)
    safe_accepted = len(accepted) - unsafe_accepted
    safe_rejected = sum(not unsafe for unsafe in rejected)
    unsafe_rejected = sum(unsafe for unsafe in rejected)
    safe_total = safe_accepted + safe_rejected

    return {
        "policy": name,
        "samples": len(decisions),
        "accepted": len(accepted),
        "acceptance_rate": (
            len(accepted) / len(decisions)
            if decisions else 0.0
        ),
        "unsafe_deployments": unsafe_accepted,
        "unsafe_rate_among_accepted": (
            unsafe_accepted / len(accepted)
            if accepted else None
        ),
        "safe_accepted": safe_accepted,
        "safe_rejected": safe_rejected,
        "unsafe_rejected": unsafe_rejected,
        "safe_coverage": (
            safe_accepted / safe_total
            if safe_total else 0.0
        ),
    }


rows = load_rows()
calibration = [
    row for row in rows if row["role"] == "calibration"
]
validation = [
    row for row in rows if row["role"] == "validation"
]

if not calibration or not validation:
    raise SystemExit(
        "Calibration and validation samples are both required."
    )

margin, conformal_rank = conformal_upper_quantile(
    [
        row["corrected_residual_ms"]
        for row in calibration
    ],
    ALPHA,
)

schedules = sorted({
    row["schedule"] for row in validation
})

report = {
    "artifact_role": "post_holdout_validation_recomputation",
    "historical_decision_context": (
        "holdout unseen during policy selection"
    ),
    "current_project_holdout_status": (
        "see holdout_results.json and dated provenance records"
    ),
    "calibration_samples": len(calibration),
    "validation_samples": len(validation),
    "alpha": ALPHA,
    "quantile_level": 1 - ALPHA,
    "finite_sample_conformal_rank": conformal_rank,
    "sentinel_conformal_margin_ms": margin,
    "schedules": {},
}

for schedule in schedules:
    schedule_rows = sorted(
        [
            row for row in validation
            if row["schedule"] == schedule
        ],
        key=lambda row: row["position"],
    )

    report["schedules"][schedule] = [
        summarize(
            "direct",
            [
                (True, row["unsafe"])
                for row in schedule_rows
            ],
        ),
        summarize(
            "twin_only",
            [
                (
                    row["twin_e2e_rtt_avg_ms"] <= SLA_MS,
                    row["unsafe"],
                )
                for row in schedule_rows
            ],
        ),
        summarize(
            "raw_candidate_link_sentinel",
            [
                (
                    row["corrected_prediction_ms"] <= SLA_MS,
                    row["unsafe"],
                )
                for row in schedule_rows
            ],
        ),
        summarize(
            "conformal_candidate_link_sentinel",
            [
                (
                    row["corrected_prediction_ms"] + margin
                    <= SLA_MS,
                    row["unsafe"],
                )
                for row in schedule_rows
            ],
        ),
    ]

candidate_names = [
    "raw_candidate_link_sentinel",
    "conformal_candidate_link_sentinel",
]
candidates: list[dict] = []

for name in candidate_names:
    aggregate = {
        "policy": name,
        "samples": 0,
        "accepted": 0,
        "unsafe_deployments": 0,
        "safe_accepted": 0,
        "safe_rejected": 0,
        "unsafe_rejected": 0,
        "schedules_with_safe_acceptance": 0,
    }

    for schedule_results in report["schedules"].values():
        result = next(
            item
            for item in schedule_results
            if item["policy"] == name
        )

        for key in (
            "samples",
            "accepted",
            "unsafe_deployments",
            "safe_accepted",
            "safe_rejected",
            "unsafe_rejected",
        ):
            aggregate[key] += result[key]

        if result["safe_accepted"] > 0:
            aggregate[
                "schedules_with_safe_acceptance"
            ] += 1

    safe_total = (
        aggregate["safe_accepted"]
        + aggregate["safe_rejected"]
    )

    aggregate["acceptance_rate"] = (
        aggregate["accepted"] / aggregate["samples"]
    )
    aggregate["unsafe_rate_among_accepted"] = (
        aggregate["unsafe_deployments"]
        / aggregate["accepted"]
        if aggregate["accepted"] else None
    )
    aggregate["safe_coverage"] = (
        aggregate["safe_accepted"] / safe_total
        if safe_total else 0.0
    )
    aggregate["non_vacuous"] = (
        aggregate["accepted"] > 0
        and aggregate["safe_accepted"] > 0
    )
    aggregate["schedule_robust_utility"] = (
        aggregate["schedules_with_safe_acceptance"]
        == len(schedules)
    )

    candidates.append(aggregate)

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
            -item["safe_coverage"],
            -item["accepted"],
        ),
    )[0]

    decision = {
        "artifact_role": "post_holdout_validation_recomputation",
        "status": "policy_ready_for_freeze",
        "holdout_locked": False,
        "selected_policy": selected["policy"],
        "selection_summary": selected,
        "holdout_seen": False,
    }
else:
    decision = {
        "artifact_role": "post_holdout_validation_recomputation",
        "status": "method_revision_required",
        "holdout_locked": True,
        "reason": (
            "No candidate-link sentinel achieved "
            "non-vacuous utility across every "
            "validation schedule."
        ),
        "candidates": candidates,
        "holdout_seen": False,
    }

report["aggregate_candidates"] = candidates
report["policy_decision"] = decision
report["limitation"] = (
    "Candidate outcomes are observed for evaluation. "
    "The sentinel inputs are available before deployment."
)

validation_output = (
    results_dir / "validation_results_recomputed.json"
)
decision_output = (
    results_dir / "policy_decision_recomputed.json"
)

validation_output.write_text(
    json.dumps(report, indent=2) + "\n",
    encoding="utf-8",
)
decision_output.write_text(
    json.dumps(decision, indent=2) + "\n",
    encoding="utf-8",
)

print(json.dumps({
    "margin_ms": margin,
    "conformal_rank": conformal_rank,
    "decision": decision,
}, indent=2))
