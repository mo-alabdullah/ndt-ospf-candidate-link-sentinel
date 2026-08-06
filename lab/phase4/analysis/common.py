from __future__ import annotations

import csv
import math
from pathlib import Path

SLA_MS = 50.0
QUANTILE_LEVEL = 0.95
FIXED_MARGIN_MS = 10.0

def load_rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    for row in rows:
        for key in (
            "position",
            "delay_ms",
            "repetition",
            "ops_rtt_avg_ms",
            "twin_rtt_avg_ms",
            "rtt_residual_ms",
        ):
            row[key] = float(row[key])
        row["position"] = int(row["position"])
        row["repetition"] = int(row["repetition"])
        row["unsafe"] = (
            row["operational_unsafe_latency"].lower() == "true"
        )
    return rows

def quantile_higher(values: list[float], level: float) -> float:
    if not values:
        raise ValueError("Quantile requires at least one value.")
    ordered = sorted(values)
    index = max(
        0,
        min(len(ordered) - 1, math.ceil(level * len(ordered)) - 1),
    )
    return ordered[index]

def summarize(policy: str, decisions: list[tuple[bool, bool]]) -> dict:
    accepted = [unsafe for deploy, unsafe in decisions if deploy]
    rejected = [unsafe for deploy, unsafe in decisions if not deploy]

    unsafe_accepted = sum(accepted)
    safe_accepted = len(accepted) - unsafe_accepted
    safe_rejected = sum(not unsafe for unsafe in rejected)

    return {
        "policy": policy,
        "samples": len(decisions),
        "accepted": len(accepted),
        "acceptance_rate": (
            len(accepted) / len(decisions) if decisions else 0.0
        ),
        "unsafe_deployments": unsafe_accepted,
        "unsafe_rate_among_accepted": (
            unsafe_accepted / len(accepted) if accepted else 0.0
        ),
        "safe_accepted": safe_accepted,
        "safe_rejected": safe_rejected,
    }

def evaluate_schedule(
    rows: list[dict],
    calibration_residuals: list[float],
    windows: list[int],
) -> list[dict]:
    results: list[dict] = []

    results.append(
        summarize(
            "direct",
            [(True, row["unsafe"]) for row in rows],
        )
    )
    results.append(
        summarize(
            "twin_only",
            [
                (
                    row["twin_rtt_avg_ms"] <= SLA_MS,
                    row["unsafe"],
                )
                for row in rows
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
                for row in rows
            ],
        )
    )

    static_margin = quantile_higher(
        calibration_residuals,
        QUANTILE_LEVEL,
    )
    static_result = summarize(
        "static_residual_quantile",
        [
            (
                row["twin_rtt_avg_ms"] + static_margin <= SLA_MS,
                row["unsafe"],
            )
            for row in rows
        ],
    )
    static_result["margin_ms"] = static_margin
    results.append(static_result)

    for window in windows:
        history = list(calibration_residuals)
        decisions: list[tuple[bool, bool]] = []
        margins: list[float] = []

        for row in rows:
            margin = quantile_higher(
                history[-window:],
                QUANTILE_LEVEL,
            )
            deploy = (
                row["twin_rtt_avg_ms"] + margin <= SLA_MS
            )
            decisions.append((deploy, row["unsafe"]))
            margins.append(margin)

            # Offline full-feedback baseline.
            history.append(row["rtt_residual_ms"])

        result = summarize(
            f"rolling_window_{window}_full_feedback",
            decisions,
        )
        result["mean_margin_ms"] = sum(margins) / len(margins)
        results.append(result)

    return results
