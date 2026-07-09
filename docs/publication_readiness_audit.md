# Publication Gate Blocker Audit

This audit aggregates evidence gates. It does not validate operational routing or certify real emergency operations.

This is a claim-scope audit only. It is not a formal acceptance record, calibrated validation, or operational route approval.

- Publication ready: `false`
- Verdict: `final_study_claims_blocked`
- Unblocked gates: 8 / 10
- Blocked gates: 2 / 10
- Can mark complete: `false`

## Evidence Gates

| Gate | Evidence status |
| --- | --- |
| `parameter_evidence_ready` | `true` |
| `road_input_evidence_ready` | `true` |
| `road_override_evidence_ready` | `true` |
| `road_override_application_ready` | `true` |
| `rail_service_evidence_ready` | `true` |
| `rail_station_binding_ready` | `true` |
| `rail_source_decision_ready` | `false` |
| `rail_transit_stress_profile_ready` | `true` |
| `rail_bounded_treatment_integrity_ready` | `true` |
| `rail_evidence_ready` | `false` |

`rail_station_binding_ready` is an identifier-binding prerequisite only; it does not prove rail timing, capacity, availability, or operational rail service.

## Remaining Blockers

- blocked requirement: road input evidence: treat this as road-input evidence only; route plausibility and traffic validation remain separate gates
- blocked requirement: road override evidence: verify graph-adapter runs apply the reviewed override table before using road-calibration claims
- blocked requirement: rail source decision: rail source decisions are not recorded as reviewed decisions
- blocked requirement: rail source decision: rail source decisions are not complete for every rail source-decision row
- blocked requirement: rail source decision: 3 rail timing source decision rows are blocked
- blocked requirement: rail source decision: 3 rail capacity or availability source decisions need human review
- blocked requirement: rail source decision: rail source-decision manifest is not publication-ready evidence
- blocked requirement: rail source decision: rail source-decision manifest cannot mark complete
- blocked requirement: rail source decision: rail source-decision manifest cannot support publication gate
- blocked requirement: rail source decision: rail source-decision manifest cannot support rail evidence gate
- blocked requirement: rail source decision: rail source-decision manifest does not accept source-backed rail service evidence
- blocked requirement: rail source decision: rail source-decision manifest has zero rail-service evidence gate closure candidates
- blocked requirement: rail source decision: non-formal rail source-decision action ledger cannot close rail evidence gate
- blocked requirement: rail source decision: rail source-decision action ledger is not formal acceptance evidence
