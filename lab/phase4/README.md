# Phase 4 — Schedule Robustness and Holdout Evaluation

Phase 4 tests whether the Phase 3 finding survives changes in the order and
pattern of drift.

## Experimental roles

- **Calibration:** independent randomized set used to estimate the initial
  residual distribution.
- **Validation:** three randomized schedules, an abrupt shift, and an
  up/down schedule. These are used to compare rolling windows.
- **Holdout:** an untouched randomized schedule used only after the rolling
  window is fixed.

## 1. Generate schedules

```bash
cd lab/phase4
python3 schedules/generate_schedules.py
```

## 2. Run calibration and validation

```bash
chmod +x scripts/*.sh
./scripts/run_validation_schedules.sh
```

Outputs:

```text
processed-data/phase4_dataset.csv
lab/phase4/results/validation_results.json
lab/phase4/results/selected_policy.json
```

## 3. Freeze the selected policy

Review `selected_policy.json`. Do not edit the selected window after
examining the holdout.

Commit the file to Git before running the holdout:

```bash
git add lab/phase4/results/selected_policy.json
git commit -m "Freeze Phase 4 rolling window before holdout"
```

## 4. Run the untouched holdout

```bash
./scripts/run_holdout.sh
```

Final output:

```text
lab/phase4/results/holdout_results.json
```

## Resume behavior

Existing samples are skipped, so a stopped schedule can be restarted.

## Scientific limitation

The rolling evaluation remains an offline full-feedback baseline. It learns
the realized residual after every candidate, including candidates it would
reject. The preprint must describe this limitation explicitly.
