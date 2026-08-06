from __future__ import annotations

import json
from pathlib import Path
import re
import sys

if len(sys.argv) != 8:
    raise SystemExit(
        "Usage: parse_sample.py <directory> <schedule> <position> "
        "<delay-ms> <repetition> <role> <seed>"
    )

directory = Path(sys.argv[1])
schedule = sys.argv[2].strip()
position = int(sys.argv[3])
delay_ms = float(sys.argv[4])
repetition = int(sys.argv[5])
role = sys.argv[6].strip()
seed = sys.argv[7].strip()

def parse_ping(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    loss = re.search(r"(\d+(?:\.\d+)?)% packet loss", text)
    rtt = re.search(
        r"(?:rtt|round-trip) min/avg/max"
        r"(?:/(?:mdev|stddev))? = "
        r"([\d.]+)/([\d.]+)/([\d.]+)"
        r"(?:/([\d.]+))? ms",
        text,
    )
    if not loss or not rtt:
        tail = "\n".join(text.splitlines()[-8:])
        raise ValueError(
            f"Could not parse {path}. Last lines:\n{tail}"
        )
    return {
        "packet_loss_percent": float(loss.group(1)),
        "rtt_min_ms": float(rtt.group(1)),
        "rtt_avg_ms": float(rtt.group(2)),
        "rtt_max_ms": float(rtt.group(3)),
        "rtt_variation_ms": (
            float(rtt.group(4))
            if rtt.group(4) is not None
            else 0.0
        ),
    }

def parse_route(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    metric = re.search(r"metric\s+(\d+)", text)
    next_hop = re.search(r"\*\s+([\d.]+),\s+via\s+(\S+)", text)
    if not metric or not next_hop:
        raise ValueError(f"Could not parse {path}")
    return {
        "metric": int(metric.group(1)),
        "next_hop": next_hop.group(1),
        "interface": next_hop.group(2),
    }

ops_link = parse_ping(directory / "ops-link-probe.txt")
twin_link = parse_ping(directory / "twin-link-probe.txt")
ops_e2e = parse_ping(directory / "ops-e2e-ping.txt")
twin_e2e = parse_ping(directory / "twin-e2e-ping.txt")
ops_route = parse_route(directory / "ops-route.txt")
twin_route = parse_route(directory / "twin-route.txt")

link_delta = ops_link["rtt_avg_ms"] - twin_link["rtt_avg_ms"]
corrected_prediction = (
    twin_e2e["rtt_avg_ms"] + max(0.0, link_delta)
)
corrected_residual = (
    ops_e2e["rtt_avg_ms"] - corrected_prediction
)

result = {
    "sample_id": directory.name,
    "schedule": schedule,
    "position": position,
    "delay_ms": delay_ms,
    "repetition": repetition,
    "role": role,
    "seed": None if seed == "" else int(seed),
    "predeployment_probe": {
        "operational_link": ops_link,
        "twin_link": twin_link,
        "link_delta_ms": link_delta,
    },
    "candidate_outcome": {
        "operational_e2e": ops_e2e,
        "twin_e2e": twin_e2e,
        "operational_route": ops_route,
        "twin_route": twin_route,
    },
    "sentinel": {
        "corrected_prediction_ms": corrected_prediction,
        "corrected_residual_ms": corrected_residual,
    },
    "labels": {
        "latency_sla_ms": 50.0,
        "operational_unsafe_latency": (
            ops_e2e["rtt_avg_ms"] > 50.0
        ),
        "route_match": (
            ops_route["next_hop"] == twin_route["next_hop"]
            and ops_route["metric"] == twin_route["metric"]
        ),
    },
}

(directory / "summary.json").write_text(
    json.dumps(result, indent=2) + "\n",
    encoding="utf-8",
)
