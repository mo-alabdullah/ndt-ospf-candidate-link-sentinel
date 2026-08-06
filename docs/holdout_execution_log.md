# Holdout Execution Log

## Pre-registered policy

- Policy: `conformal_candidate_link_sentinel`
- Conformal margin: `0.661 ms`
- Holdout schedule: `holdout_seed909`
- Policy parameters changed after validation: no

## First-run incident

The first holdout sample was measured before the frozen-policy manifest
had been added to Git because the repository ignored the results
directory. Collection stopped during parsing because the FRR container
emitted a three-value `round-trip min/avg/max` summary, while the parser
required a fourth variation value.

The raw measurement files were preserved. No threshold, margin,
prediction rule, schedule, or policy parameter was changed. The parser
was extended only to accept both three-value and four-value ping
summaries.

## Recovery rule

Parse the existing first-sample files rather than remeasure them.
Resume the same holdout schedule. Do not tune the policy after viewing
holdout outcomes.
