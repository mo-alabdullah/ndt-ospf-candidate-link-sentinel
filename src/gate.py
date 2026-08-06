"""Residual-quantile deployment gates.

This module intentionally provides a transparent baseline implementation.
Formal conformal or selective-risk guarantees must not be claimed without
checking their assumptions and implementing the corresponding method.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence
import math


@dataclass(frozen=True)
class GateDecision:
    deploy: bool
    upper_bounds: dict[str, float]
    reason: str


def empirical_quantile(values: Sequence[float], level: float) -> float:
    """Return a conservative empirical quantile using the higher order statistic."""
    if not values:
        raise ValueError("Calibration residuals must not be empty.")
    if not 0.0 < level <= 1.0:
        raise ValueError("Quantile level must be in (0, 1].")
    ordered = sorted(float(v) for v in values)
    index = max(0, min(len(ordered) - 1, math.ceil(level * len(ordered)) - 1))
    return ordered[index]


def rolling_quantile_gate(
    predictions: Mapping[str, float],
    residual_history: Mapping[str, Sequence[float]],
    sla_limits: Mapping[str, float],
    risk_level: float = 0.05,
    window: int = 50,
    logical_checks_passed: bool = True,
) -> GateDecision:
    """Gate a change using recent upper residual quantiles.

    Residuals are defined as observed_value - predicted_value. Positive
    residuals mean the twin was optimistic.
    """
    if not logical_checks_passed:
        return GateDecision(False, {}, "logical_verification_failed")
    if not 0.0 < risk_level < 1.0:
        raise ValueError("risk_level must be in (0, 1).")
    if window <= 0:
        raise ValueError("window must be positive.")

    upper_bounds: dict[str, float] = {}
    for metric, limit in sla_limits.items():
        if metric not in predictions:
            return GateDecision(False, upper_bounds, f"missing_prediction:{metric}")
        history = list(residual_history.get(metric, []))[-window:]
        if not history:
            return GateDecision(False, upper_bounds, f"insufficient_calibration:{metric}")
        margin = empirical_quantile(history, 1.0 - risk_level)
        upper_bounds[metric] = float(predictions[metric]) + margin
        if upper_bounds[metric] > float(limit):
            return GateDecision(False, upper_bounds, f"sla_risk:{metric}")

    return GateDecision(True, upper_bounds, "all_conservative_bounds_within_sla")
