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
schedule = sys.argv[2]
position = int(sys.argv[3])
delay_ms = float(sys.argv[4])
repetition = int(sys.argv[5])
role = sys.argv[6]
seed = sys.argv[7]

def parse_ping(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    loss = re.search(r"(\d+(?:\.\d+)?)% packet loss", text)
    rtt = re.search(
        r"(?:rtt|round-trip) min/avg/max/(?:mdev|stddev) = "
        r"([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+) ms",
        text,
    )
    if not loss or not rtt:
        raise ValueError(f"Could not parse {path}")
    return {
        "packet_loss_percent": float(loss.group(1)),
        "rtt_min_ms": float(rtt.group(1)),
        "rtt_avg_ms": float(rtt.group(2)),
        "rtt_max_ms": float(rtt.group(3)),
        "rtt_variation_ms": float(rtt.group(4)),
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

ops_ping = parse_ping(directory / "ops-ping.txt")
twin_ping = parse_ping(directory / "twin-ping.txt")
ops_route = parse_route(directory / "ops-route.txt")
twin_route = parse_route(directory / "twin-route.txt")

result = {
    "sample_id": directory.name,
    "schedule": schedule,
    "position": position,
    "delay_ms": delay_ms,
    "repetition": repetition,
    "role": role,
    "seed": None if seed == "" else int(seed),
    "operational": {
        **ops_ping,
        "route": ops_route,
    },
    "twin": {
        **twin_ping,
        "route": twin_route,
    },
    "residuals": {
        "rtt_avg_ms": (
            ops_ping["rtt_avg_ms"] - twin_ping["rtt_avg_ms"]
        ),
        "packet_loss_percent": (
            ops_ping["packet_loss_percent"]
            - twin_ping["packet_loss_percent"]
        ),
    },
    "labels": {
        "latency_sla_ms": 50.0,
        "operational_unsafe_latency": (
            ops_ping["rtt_avg_ms"] > 50.0
        ),
        "twin_predicted_safe_latency": (
            twin_ping["rtt_avg_ms"] <= 50.0
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
