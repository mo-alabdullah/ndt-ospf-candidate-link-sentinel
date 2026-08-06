# Phase 1: OSPF Smoke Test

This validates the experimental stack before building the operational-network
and digital-twin pair.

## Run

```bash
cd lab/smoke-test
chmod +x scripts/*.sh
./scripts/deploy.sh
./scripts/verify.sh
```

Initially, the direct r1-r3 link costs 30 while the route through r2 costs 20.
Apply a controlled change:

```bash
./scripts/change_cost.sh
```

The direct link then costs 5 and the selected route should change.

Restore and destroy:

```bash
./scripts/reset_cost.sh
./scripts/destroy.sh
```

## Acceptance criteria

- Each router forms two OSPF adjacencies.
- h1 reaches h3.
- The r1-to-h3 route changes after the cost update.
- Unedited command outputs are stored in the research journal.
