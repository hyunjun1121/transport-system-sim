# Publication Readiness Audit

This audit aggregates evidence-readiness gates. It does not validate operational routing or certify real emergency operations.

This is a claim-readiness audit only. It is not a formal acceptance record, calibrated validation, or operational route approval.

- Publication ready: `false`
- Verdict: `final_study_claims_blocked`
- Ready gates: 1 / 7
- Blocked gates: 6 / 7
- Can mark complete: `false`

## Evidence Gates

| Gate | Ready |
| --- | --- |
| `parameter_evidence_ready` | `false` |
| `road_input_evidence_ready` | `false` |
| `road_override_evidence_ready` | `false` |
| `road_override_application_ready` | `false` |
| `rail_service_evidence_ready` | `false` |
| `rail_station_binding_ready` | `true` |
| `rail_evidence_ready` | `false` |

## Remaining Blockers

- parameter evidence: justify demand scale, arrival process, time horizon, and censoring penalties with planning assumptions or sensitivity-bound evidence
- parameter evidence: replace scenario-only disruption probabilities and degradation rules with public hazard, incident, literature, or expert-reviewed evidence
- parameter evidence: replace generic fleet and vehicle-capacity assumptions with agency, planning, literature, or accepted scenario evidence
- parameter evidence: derive rail headway and travel time from cached GTFS, timetable, operator, or agency records, and keep rail capacity source-backed or explicitly sensitivity-only
- parameter evidence: strengthen road speed, capacity, and background traffic values with public speed limits, traffic counts, or benchmark-calibrated routing
- parameter evidence: support transfer delays with station-layout evidence, observed ranges, or literature rather than generic fixed delays
- road input evidence: review OSM maxspeed coverage and replace fallback free-flow speeds where final claims require calibration
- road input evidence: replace road-class capacity proxies with traffic counts, agency capacity references, or benchmark-calibrated values
- road input evidence: replace road-class base disruption probabilities with hazard, incident, or accepted scenario evidence
- road input evidence: treat this as road-input evidence only; route plausibility and traffic validation remain separate gates
- road override evidence: replace the draft road-class override worksheet with a reviewed road_class_overrides.csv table containing source-backed speed, capacity, and base-disruption evidence
- road override evidence: apply the reviewed overrides when adapting the pilot graph if final claims require calibrated road inputs
- road override application: reviewed road-class override table is absent
- rail service evidence: cache timetable, shortest-path, or GTFS-derived records
- rail service evidence: derive headway and travel time from the cached records
