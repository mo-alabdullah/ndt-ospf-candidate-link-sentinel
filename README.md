# When the Network Twin Drifts: A Candidate-Link Sentinel for Safe OSPF Reconfiguration

Reproducibility workspace for the sole-authored preprint by Mohammed Alabdullah.

- ORCID: 0009-0001-0826-4380
- Correspondence: m.w@sudo-gate.com
- Affiliation: Department of Network Engineering, School of Computer Engineering, Iran University of Science and Technology (IUST), Tehran, Iran
- Release: v1.0.0

## Research question

The study asks whether a network digital twin can approve an OSPF link-cost change even when hidden operational latency on the activated link makes the resulting path violate a 50 ms service-level objective.

## Main empirical result

The frozen candidate-link sentinel accepted 110 of 186 validation candidates, including 109 safe candidates, with one unsafe deployment. On the untouched 33-sample holdout, it accepted all 19 safe candidates and rejected all 14 unsafe candidates. The holdout result is empirical; the one-sided score covered only 20 of 33 realized RTTs and does not establish nominal conformal coverage under distribution shift.

## Repository layout

- `paper/`: final manuscript, LaTeX source, references, and review PDF.
- `lab/`: Containerlab/FRRouting configurations, scripts, schedules, and frozen result records.
- `processed-data/`: analysis-ready Phase 3--5 datasets.
- `results/`: Phase 3 summaries.
- `figures/`: manuscript figures.
- `docs/`: design, provenance, correction, and traceability records.
- `tools/verify_release.py`: read-only verification.

## Integrity constraints

Do not rerun, overwrite, or tune against the Phase 5 holdout. Do not modify `lab/phase5/results/frozen_policy.json`. See `lab/phase5/results/frozen_hash_resolution.json`.

## Quick verification

```bash
python3 tools/verify_release.py
```

The verifier writes no experimental result files.

## Public release artifacts

- Manuscript source is distributed separately for arXiv upload.
- Reproducibility artifact: `ndt-ospf-artifact-v1.0.0.zip`
- License: MIT for software and artifact files
