# Phase 3 — Delay Sweep and Initial Gate Evaluation

Phase 3 turns the successful single drift experiment into a repeated
dataset.

## Preconditions

Keep both Phase 2 labs running and verify them first:

```bash
cd ../phase2
./scripts/verify_both.sh
```

## Collect the dataset

```bash
cd ../phase3
chmod +x scripts/*.sh
REPETITIONS=5 ./scripts/run_delay_sweep.sh
```

The default sweep uses 11 per-direction delay levels and five repetitions,
producing 55 samples.

## Outputs

Raw evidence:

```text
raw-data/phase2/
```

Consolidated dataset:

```text
processed-data/phase3_delay_sweep.csv
```

Initial policy evaluation:

```text
results/phase3_gate_summary.json
```

## Scientific caution

The rolling policy is evaluated through offline full-feedback replay. This
means the realized residual is available even for a change that the policy
would have rejected. It is an informative baseline but not the final
selective-feedback method proposed for the journal extension.
