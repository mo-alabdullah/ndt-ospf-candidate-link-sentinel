# Phase 5 — Candidate-Link Drift Sentinel

Phase 5 measures the candidate link before deploying the OSPF cost change.

## Run calibration and validation

```bash
cd lab/phase5
chmod +x scripts/*.sh
./scripts/run_validation.sh
```

Existing Phase 2 labs are reused. Completed Phase 5 samples are skipped on
restart.

## Outputs

```text
processed-data/phase5_sentinel_dataset.csv
lab/phase5/results/validation_results.json
lab/phase5/results/policy_decision.json
```

## Decision rule

Do not run the holdout unless `policy_decision.json` contains:

```json
{
  "status": "policy_ready_for_freeze",
  "holdout_locked": false,
  "holdout_seen": false
}
```

Even then, freeze the decision in Git and review it before enabling the
holdout runner.


## Frozen Phase 5 policy

The validation-selected conformal candidate-link sentinel is frozen in:

```text
results/frozen_policy.json
```

The finite-sample conformal margin is 0.661 ms. Commit the frozen policy
before running the untouched holdout:

```bash
git add results/frozen_policy.json
git commit -m "Freeze Phase 5 sentinel before holdout"
```

Then run exactly once:

```bash
./scripts/run_holdout.sh
```

The runner refuses a second completed holdout evaluation.
