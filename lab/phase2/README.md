# Phase 2 — Operational Network and Digital Twin

Creates two isolated, initially identical OSPF labs: `ospf-ops` and
`ospf-twin`. The first experiment introduces hidden delay on the direct r1-r3
link in the operational network only, then applies the same OSPF change to
both systems.

## Run

```bash
cd lab/phase2
chmod +x scripts/*.sh
./scripts/deploy_both.sh
./scripts/verify_both.sh
./scripts/run_first_drift_experiment.sh
```

Outputs are stored under `raw-data/phase2/` with a parsed `summary.json`.
Expected qualitatively: low baseline residual, then a large positive RTT
residual after operational-only drift. Use only recorded values in the paper.

## Cleanup

```bash
./scripts/destroy_both.sh
```
