# Reproducibility Correction — Phase 5 Evaluator

During preparation of the System and Method sections, the bundled
`evaluate_sentinel.py` was found to contain two stale fragments:

1. the pre-correction quantile function; and
2. a reference to an undefined `conformal_rank` variable.

The validation data, frozen policy, and holdout results were not changed. The
evaluator was replaced with a finite-sample one-sided order-statistic
implementation:

```text
rank = ceil((n + 1) * (1 - alpha))
```

For 22 calibration samples and alpha 0.05, it reproduces rank 22 and margin
0.661 ms. The selected policy remains
`conformal_candidate_link_sentinel`.

The original validation result files remain available with the `_original`
suffix. Newly generated `validation_results.json` and `policy_decision.json`
are reproducible corrected outputs.


## Output-file semantics update

A later reproducibility review identified that rerunning the evaluator
after holdout completion could overwrite files whose `holdout_seen: false`
value describes the historical validation decision. The evaluator now
writes `validation_results_recomputed.json` and
`policy_decision_recomputed.json` by default.

The canonical validation artifacts remain unchanged. The recomputed files
are labeled as post-holdout validation reproductions and point readers to
`holdout_results.json` for the current experimental state.
