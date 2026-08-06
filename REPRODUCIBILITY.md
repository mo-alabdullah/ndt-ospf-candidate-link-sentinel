# Reproducibility Guide

## Recorded environment

- Containerlab 0.77.0
- FRRouting image: `quay.io/frrouting/frr:10.5.1`
- Host image: `wbitt/network-multitool:3.22.2`
- Ubuntu guest provided by OrbStack on Apple silicon

## Experimental phases

Phase 4 and Phase 5 share schedule definitions and sample counts but are
independent measurement runs. Phase 5 opens one 33-sample holdout after policy
freezing.

## Measurement protocol

Each sample restores baseline cost, collects 20 operational and 20 twin link
probes, applies candidate cost 5, waits two seconds, captures routing state,
and collects 20 end-to-end probes. The probe interval is 0.1 s and the
response timeout is 2 s.

## Verification

```bash
python3 tools/verify_release.py
```

The verifier checks recorded calculations and hashes. It does not rerun the
holdout. New experiments must use new output directories and must not replace
canonical Phase 5 artifacts.
