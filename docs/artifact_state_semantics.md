# Artifact State Semantics

## Purpose

Several JSON files describe the state of the experiment at different points in
time. Their Boolean fields must be interpreted according to the role of the
artifact, not as a single mutable project-status flag.

## Validation-stage artifacts

`lab/phase5/results/policy_decision.json` records the decision produced from
calibration and validation data. In that historical decision context:

```json
"holdout_seen": false
```

is correct: the policy-selection procedure did not use the holdout.

Running the validation evaluator after the holdout does not make the validation
decision itself depend on the holdout. However, newly generated files should
not overwrite the canonical historical artifact without being labeled as
recomputations.

## Frozen policy manifest

`lab/phase5/results/frozen_policy.json` records the parameters fixed for the
one-time holdout. Its `holdout_seen: false` field describes the state at the
time of freezing. The manifest is intentionally immutable and is not updated
after evaluation.

## Holdout result

`lab/phase5/results/holdout_results.json` is the authoritative evidence that
the holdout was executed. It contains:

```json
"evaluation": "untouched_holdout"
```

and the 33 holdout records. This file, the holdout dataset, the execution log,
and the dated provenance records establish the current project state.

## Recomputed validation outputs

The corrected evaluator now writes:

```text
validation_results_recomputed.json
policy_decision_recomputed.json
```

These files are reproducibility checks. They contain:

```json
"artifact_role": "post_holdout_validation_recomputation"
```

and must not be interpreted as claiming that the overall project has not seen
the holdout.

## Publication wording

Use:

> The holdout was unseen during calibration and policy selection.

Do not use:

> The holdout is currently unseen.

The first statement describes experimental independence. The second is false
after holdout execution.
