#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import csv, hashlib, json, math

ROOT = Path(__file__).resolve().parents[1]
SLA = 50.0
MARGIN = 0.6610000000000014

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def rows(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def mean(values):
    return sum(values) / len(values)

def pearson(xs, ys):
    mx, my = mean(xs), mean(ys)
    num = sum((x-mx)*(y-my) for x,y in zip(xs,ys))
    den = math.sqrt(sum((x-mx)**2 for x in xs) * sum((y-my)**2 for y in ys))
    return num / den

def evaluate(data):
    obs = [float(r["ops_e2e_rtt_avg_ms"]) for r in data]
    twin = [float(r["twin_e2e_rtt_avg_ms"]) for r in data]
    corr = [float(r["corrected_prediction_ms"]) for r in data]
    unsafe = [v > SLA for v in obs]
    accept = [v + MARGIN <= SLA for v in corr]
    raw = [v <= SLA for v in corr]
    twin_accept = [v <= SLA for v in twin]
    safe = sum(not u for u in unsafe)
    return {
        "samples": len(data),
        "accepted": sum(accept),
        "unsafe_deployments": sum(a and u for a,u in zip(accept,unsafe)),
        "safe_accepted": sum(a and not u for a,u in zip(accept,unsafe)),
        "safe_rejected": sum((not a) and (not u) for a,u in zip(accept,unsafe)),
        "unsafe_rejected": sum((not a) and u for a,u in zip(accept,unsafe)),
        "safe_coverage": sum(a and not u for a,u in zip(accept,unsafe))/safe,
        "raw_accepted": sum(raw),
        "raw_unsafe": sum(a and u for a,u in zip(raw,unsafe)),
        "twin_accepted": sum(twin_accept),
        "twin_unsafe": sum(a and u for a,u in zip(twin_accept,unsafe)),
        "corrected_mae": mean([abs(y-p) for y,p in zip(obs,corr)]),
        "twin_mae": mean([abs(y-p) for y,p in zip(obs,twin)]),
        "upper_coverage": sum(y <= p+MARGIN for y,p in zip(obs,corr))/len(data),
        "pearson": pearson(corr,obs),
        "route_agreement": sum(r["route_match"].lower()=="true" for r in data),
    }

frozen_path = ROOT/"lab/phase5/results/frozen_policy.json"
frozen = json.loads(frozen_path.read_text())
resolution = json.loads((ROOT/"lab/phase5/results/frozen_hash_resolution.json").read_text())
dataset = ROOT/"processed-data/phase5_sentinel_dataset.csv"
assert sha256(dataset) == frozen["source_sha256"]["phase5_sentinel_dataset.csv"]
for item in resolution["mappings"]:
    p = ROOT/"lab/phase5/results"/item["preserved_historical_filename"]
    assert sha256(p) == item["expected_sha256"]

validation = evaluate([r for r in rows(dataset) if r["role"] == "validation"])
holdout = evaluate(rows(ROOT/"processed-data/phase5_holdout_dataset.csv"))

for key,value in {
    "samples":186,"accepted":110,"unsafe_deployments":1,"safe_accepted":109,
    "safe_rejected":3,"unsafe_rejected":73,"raw_accepted":111,"raw_unsafe":2,
    "twin_accepted":186,"twin_unsafe":74,"route_agreement":186
}.items():
    assert validation[key] == value, (key, validation[key], value)
for key,value in {
    "samples":33,"accepted":19,"unsafe_deployments":0,"safe_accepted":19,
    "safe_rejected":0,"unsafe_rejected":14,"raw_accepted":20,"raw_unsafe":1,
    "twin_accepted":33,"twin_unsafe":14,"route_agreement":33
}.items():
    assert holdout[key] == value, (key, holdout[key], value)

print(json.dumps({
    "status":"PASS",
    "frozen_policy_sha256":sha256(frozen_path),
    "validation":validation,
    "holdout":holdout,
}, indent=2))
