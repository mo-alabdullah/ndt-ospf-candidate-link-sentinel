# Research Protocol v0.1

## 1. Working title

**When the Network Twin Drifts: Risk-Calibrated Validation of OSPF Reconfigurations**

## 2. Research objective

Design and evaluate a deployment gate that uses recent errors between a
Network Digital Twin and an operational network to decide whether a candidate
OSPF link-weight reconfiguration should be deployed.

## 3. Research question

How reliably can residual-based risk calibration prevent unsafe OSPF
reconfigurations when the NDT is affected by traffic, topology, link-property,
and telemetry-freshness drift?

## 4. Hypotheses

- **H1:** A rolling residual-quantile gate lowers unsafe deployment rate
  compared with direct deployment, twin-only thresholding, and a fixed margin.
- **H2:** Rolling calibration adapts better than static calibration under
  moderate non-stationary drift.
- **H3:** The safety gain does not require rejecting nearly all useful changes;
  acceptance rate and safe-change rejection must therefore be reported.
- **H4:** Logical verification and performance-risk calibration are
  complementary: reachability checks prevent logical faults, while the gate
  handles latency, loss, and utilization uncertainty.

## 5. Scope constraints

### Included

- OSPFv2.
- Link-weight changes.
- Single administrative domain.
- IPv4.
- Three reproducible public backbone topologies.
- Emulated operational network and separately instantiated NDT.
- End-to-end latency, packet loss, maximum link utilization, and reachability.
- Deploy/Reject policy.

### Deferred to journal extension

- automation-generated changes.
- Canary deployment.
- Selective conformal guarantees.
- Partial-feedback correction.
- BGP and Segment Routing.
- Hardware testbed validation.
- Multi-domain control.

## 6. Experimental platforms

### Operational network

- Containerlab.
- FRRouting routers.
- Linux traffic generators and receivers.
- `tc/netem` for controlled latency, bandwidth, and loss.
- Prometheus-compatible or structured JSON/CSV telemetry.

### Network digital twin

A separate topology instance initialized from the operational network, then
perturbed to introduce controlled fidelity gaps.

## 7. Topologies

Use three topologies with increasing size:

1. Abilene.
2. GEANT.
3. GARR.

Record the exact source file, preprocessing script, node count, edge count,
and any removed parallel links or isolated nodes.

## 8. Candidate OSPF changes

For each traffic matrix:

1. Identify the most utilized link.
2. Generate candidate weight changes around links on congested shortest paths.
3. Recompute shortest paths in the NDT.
4. Rank candidates by predicted maximum-link-utilization reduction.
5. Submit the top candidate to each deployment policy.

The same candidate must be evaluated by all policies for a fair comparison.

## 9. Drift scenarios

### D0 — No drift
Twin and operational network remain synchronized.

### D1 — Traffic-volume drift
Scale selected demands by controlled factors.

### D2 — Traffic-locality drift
Move traffic toward a new hotspot pair or region.

### D3 — Link-capacity drift
Reduce capacity of one or more operational links without immediately updating
the twin.

### D4 — Link-latency drift
Increase operational delay on selected links.

### D5 — Topology drift
Fail one operational link while the twin retains the previous topology.

### D6 — Telemetry staleness
Build the twin from measurements delayed by a controlled number of intervals.

### D7 — Compound drift
Combine traffic and link-property drift.

Each drift type is evaluated at mild, moderate, and severe levels.

## 10. Safety definition

A deployed change is unsafe if any condition holds during the evaluation
window:

- End-to-end latency exceeds its SLA threshold.
- Packet loss exceeds its SLA threshold.
- Maximum link utilization exceeds its operational threshold.
- Required reachability is lost.
- A routing loop or blackhole is detected.
- Emergency rollback is triggered.

Thresholds must be declared before viewing test results.

## 11. Deployment policies

### B0 — Direct
Deploy every proposed change.

### B1 — Twin-only
Deploy when all point predictions from the twin satisfy the SLA.

### B2 — Fixed margin
Deploy when each predicted metric plus a manually selected fixed margin
satisfies the SLA.

### B3 — Static residual quantile
Estimate an upper residual quantile on a fixed calibration set.

### P — Rolling residual quantile
Estimate an upper residual quantile from a recent rolling window, optionally
weighted by recency.

For metric \(k\):

\[
U_{t,k}=\hat{y}_{t,k}+q_{t,k}
\]

Deploy only when:

\[
U_{t,k}\leq \tau_k \quad \forall k
\]

and logical verification passes.

This preprint should describe the method as residual-quantile risk calibration
unless its formal assumptions and guarantees are fully proved.

## 12. Primary outcomes

- Unsafe Deployment Rate.
- SLA Violation Rate.
- Safe Change Acceptance Rate.
- Safe Change Rejection Rate.
- Overall Acceptance Rate.
- Mean violation severity.
- Maximum link utilization improvement.
- End-to-end latency improvement.
- Gate decision overhead.

## 13. Experimental repetitions

- Use multiple traffic matrices per topology.
- Use multiple random seeds per scenario.
- Report the number of independent runs.
- Preserve seeds and raw logs.
- Report confidence intervals, not only averages.

## 14. Required comparisons

- Compare all methods on identical candidate changes.
- Separate no-drift and drift results.
- Report risk-versus-acceptance curves.
- Report performance by topology, drift type, and severity.
- Include an ablation for rolling-window length and risk level.

## 15. Threats to validity

- Both the operational network and the twin are emulated.
- The operational environment may share host resources with the twin.
- Results may depend on traffic-generation realism.
- Residual quantiles do not automatically provide arbitrary distribution-free
  guarantees under severe temporal drift.
- Public topology graphs may not include complete capacity and delay metadata.
- OSPF weight changes represent only one class of network reconfiguration.

## 16. Reproducibility requirements

Release:

- Topology conversion scripts.
- FRR configurations.
- Traffic matrices.
- Drift injection scripts.
- Candidate generation algorithm.
- Gate implementations.
- Raw and processed measurements.
- Figure-generation scripts.
- Environment versions.
- Exact commands for every experiment.

## 17. Stop/go criteria for the preprint

Proceed to public posting only if:

- All baselines run successfully.
- Results reproduce from a clean environment.
- No result value is manually copied into figures.
- The proposed gate improves safety in more than one topology.
- Acceptance rate is reported alongside safety.
- Limitations and failed cases are disclosed.
