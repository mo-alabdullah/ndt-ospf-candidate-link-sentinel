# Experiment Logging Contract

Every evaluated candidate change must produce one immutable JSON record with:

- `experiment_id`
- `timestamp`
- `git_commit`
- `topology`
- `seed`
- `traffic_matrix_id`
- `drift_type`
- `drift_level`
- `telemetry_age_seconds`
- `candidate_change`
- `policy`
- `twin_prediction`
- `calibration_window_ids`
- `gate_decision`
- `gate_upper_bounds`
- `operational_outcome`
- `unsafe`
- `violation_severity`
- `routing_convergence_seconds`
- `gate_runtime_ms`
- `rollback_triggered`
- `software_versions`

## Fair-comparison rule

The same candidate change and the same operational scenario must be evaluated
under every policy. Do not allow each policy to receive a different candidate.

## Leakage rule

No operational outcome from a test record may enter the calibration history
used to decide that same record.

## Result-production rule

All tables and figures must be generated from raw logs through scripts. Manual
editing of result values is prohibited.
