# Publication Gate Blocker Audit

This audit aggregates evidence gates. It does not validate operational routing or certify real emergency operations.

This is a claim-scope audit only. It is not a formal acceptance record, calibrated validation, or operational route approval.

- Publication ready: `false`
- Verdict: `final_study_claims_blocked`
- Unblocked gates: 1 / 10
- Blocked gates: 9 / 10
- Can mark complete: `false`

## Evidence Gates

| Gate | Evidence status |
| --- | --- |
| `parameter_evidence_ready` | `false` |
| `road_input_evidence_ready` | `false` |
| `road_override_evidence_ready` | `false` |
| `road_override_application_ready` | `false` |
| `rail_service_evidence_ready` | `false` |
| `rail_station_binding_ready` | `true` |
| `rail_source_decision_ready` | `false` |
| `rail_transit_stress_profile_ready` | `false` |
| `rail_bounded_treatment_integrity_ready` | `false` |
| `rail_evidence_ready` | `false` |

`rail_station_binding_ready` is an identifier-binding prerequisite only; it does not prove rail timing, capacity, availability, or operational rail service.

## Remaining Blockers

- blocked requirement: parameter evidence: justify demand scale, arrival process, time horizon, and censoring penalties with planning assumptions or sensitivity-bound evidence
- blocked requirement: parameter evidence: replace scenario-only disruption probabilities and degradation rules with public hazard, incident, literature, or expert-reviewed evidence
- blocked requirement: parameter evidence: replace generic fleet and vehicle-capacity assumptions with agency, planning, literature, or accepted scenario evidence
- blocked requirement: parameter evidence: derive rail headway and travel time from cached GTFS, timetable, operator, or agency records, and keep rail capacity source-backed or explicitly sensitivity-only
- blocked requirement: parameter evidence: strengthen road speed, capacity, and background traffic values with public speed limits, traffic counts, or benchmark-calibrated routing
- blocked requirement: parameter evidence: support transfer delays with station-layout evidence, observed ranges, or literature rather than generic fixed delays
- blocked requirement: road input evidence: review OSM maxspeed coverage and replace fallback free-flow speeds where final claims require calibration
- blocked requirement: road input evidence: replace road-class capacity proxies with traffic counts, agency capacity references, or benchmark-calibrated values
- blocked requirement: road input evidence: replace road-class base disruption probabilities with hazard, incident, or accepted scenario evidence
- blocked requirement: road input evidence: treat this as road-input evidence only; route plausibility and traffic validation remain separate gates
- blocked requirement: road override evidence: replace the draft road-class override worksheet with a reviewed road_class_overrides.csv table containing source-backed speed, capacity, and base-disruption evidence
- blocked requirement: road override evidence: apply the reviewed overrides when adapting the pilot graph if final claims require calibrated road inputs
- blocked requirement: road override application: reviewed road-class override table is absent
- blocked requirement: rail service evidence: cache timetable, shortest-path, or GTFS-derived records
- blocked requirement: rail service evidence: derive headway and travel time from the cached records
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
- blocked requirement: rail transit stress profile: rail transit stress-profile manifest is not publication-ready evidence
- blocked requirement: rail transit stress profile: rail transit stress-profile manifest cannot mark complete
- blocked requirement: rail transit stress profile: rail transit stress-profile manifest cannot support rail evidence gate
- blocked requirement: rail transit stress profile: rail transit stress profiles are scenario/sensitivity review support only
- blocked requirement: rail transit stress profile: capacity and availability profiles require reviewer decisions before release-scope rail claims
- blocked requirement: rail transit stress profile: rail source decision: rail source decisions are pending for timetable, shortest-path, GTFS, capacity, and availability requests
- blocked requirement: rail transit stress profile: rail source decision: rail timing cache or reviewed GTFS source files remain required for source-backed timing claims
- blocked requirement: rail transit stress profile: rail source decision: retained rail capacity and availability assumptions require source-backed updates, sensitivity-only limits, scenario-only limits, or reviewer-scoped bounded treatment
- blocked requirement: rail transit stress profile: rail source decision: non-formal source decisions do not close rail evidence, publication, study-closeout, or formal decision gates
- blocked requirement: rail transit stress profile: rail source decision: rail_shortest_path_travel_time_request: DATA_GO_KR_KEY is absent and no cached payload is present
- blocked requirement: rail transit stress profile: rail source decision: rail_static_gtfs_timing_request: reviewed GTFS file or GTFS Validator report is absent
- blocked requirement: rail transit stress profile: rail source decision: rail_timetable_headway_request: DATA_GO_KR_KEY is absent and no cached payload is present
- blocked requirement: rail bounded treatment: 4 rail bounded-treatment warnings remain
- blocked requirement: rail bounded treatment: 2 rail bounded-treatment source decisions remain pending
