# When the Network Twin Drifts: A Candidate-Link Sentinel for Safe OSPF Reconfiguration

Reproducibility workspace for the sole-authored manuscript by Mohammed Alabdullah.

- ORCID: 0009-0001-0826-4380
- Correspondence: m.w@sudo-gate.com
- Affiliation: Department of Network Engineering, School of Computer Engineering, Iran University of Science and Technology (IUST), Tehran, Iran
- Release: v1.0.0

## Submission-ready manuscript

The canonical manuscript source in `paper/main.tex` and `paper/sections/` is synchronized with the finalized IEEE Transactions on Network and Service Management (TNSM) submission version after the final independent review pass.

- Initial submission target: 9 pages in IEEE two-column format.
- `paper/manuscript.pdf` is rebuilt from the canonical source by GitHub Actions and is required to remain 9 pages.
- The finalized manuscript uses SLO terminology consistently, qualifies the holdout reporting, strengthens the transferable-design-pattern framing, uses the corrected February 2026 IETF draft revisions, and contains the minimized truthful AI-use acknowledgment.
- Experimental measurements, frozen-policy parameters, validation/holdout outcomes, and scientific results are unchanged.

## Research question

The study asks whether a network digital twin can approve an OSPF link-cost
change even when hidden operational latency on the activated link makes the
resulting path violate a 50 ms service-level objective.

## Main empirical result

The frozen candidate-link sentinel accepted 110 of 186 validation candidates,
including 109 safe candidates, with one unsafe deployment. On the 33-sample
holdout, it accepted all 19 safe candidates and rejected all 14 unsafe
candidates. The holdout result is empirical; the one-sided score covered only
20 of 33 realized RTTs and does not establish nominal conformal coverage under
distribution shift.

## Repository layout

- `paper/`: finalized manuscript source, generated PDF, references, and figures.
- `paper/sections/`: section-level LaTeX source used by the canonical manuscript.
- `lab/`: Containerlab/FRRouting configurations, scripts, schedules, and
  frozen result records.
- `processed-data/`: analysis-ready Phase 3--5 datasets.
- `results/`: Phase 3 summaries.
- `figures/`: manuscript figures.
- `docs/`: design, provenance, correction, and traceability records.
- `tools/verify_release.py`: read-only verification.

## Integrity constraints

Do not rerun, overwrite, or tune against the Phase 5 holdout. Do not modify
`lab/phase5/results/frozen_policy.json`. See
`lab/phase5/results/frozen_hash_resolution.json`.

## Quick verification

```bash
python3 tools/verify_release.py
```

The verifier writes no experimental result files.

## Public release artifacts

- Reproducibility artifact: `ndt-ospf-artifact-v1.0.0.zip`
- License: MIT for software and artifact files

## Archived release

- Version DOI: https://doi.org/10.5281/zenodo.21821039
- Concept DOI: https://doi.org/10.5281/zenodo.21821038
- Source repository: https://github.com/mo-alabdullah/ndt-ospf-candidate-link-sentinel
- GitHub release: `v1.0.0`
