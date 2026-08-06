"""Metrics and safety-label helpers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Outcome:
    latency_ms: float
    packet_loss_fraction: float
    maximum_link_utilization: float
    reachability_ok: bool
    routing_loop_detected: bool
    rollback_triggered: bool


@dataclass(frozen=True)
class Sla:
    latency_ms: float = 50.0
    packet_loss_fraction: float = 0.01
    maximum_link_utilization: float = 0.85


def is_unsafe(outcome: Outcome, sla: Sla) -> bool:
    return any(
        [
            outcome.latency_ms > sla.latency_ms,
            outcome.packet_loss_fraction > sla.packet_loss_fraction,
            outcome.maximum_link_utilization > sla.maximum_link_utilization,
            not outcome.reachability_ok,
            outcome.routing_loop_detected,
            outcome.rollback_triggered,
        ]
    )


def violation_severity(outcome: Outcome, sla: Sla) -> float:
    ratios = [
        max(0.0, outcome.latency_ms - sla.latency_ms) / max(sla.latency_ms, 1e-12),
        max(0.0, outcome.packet_loss_fraction - sla.packet_loss_fraction)
        / max(sla.packet_loss_fraction, 1e-12),
        max(0.0, outcome.maximum_link_utilization - sla.maximum_link_utilization)
        / max(sla.maximum_link_utilization, 1e-12),
    ]
    if not outcome.reachability_ok or outcome.routing_loop_detected:
        ratios.append(1.0)
    if outcome.rollback_triggered:
        ratios.append(1.0)
    return min(1.0, max(ratios, default=0.0))
