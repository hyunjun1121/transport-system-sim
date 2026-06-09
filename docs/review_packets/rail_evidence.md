# Rail Evidence Review Packet

Sub-agent records are review aids. They do not replace formal acceptance artifacts, source-backed reviewer decisions, calibrated validation, or operational routing approval.

- Gate ID: `rail_evidence`
- Agent: `Road / Rail / Parameter Evidence Agent`
- Status: `blocked`
- Can mark complete: `false`
- Generated at: `2026-06-03T08:36:37+00:00`

## Decision

Road / Rail / Parameter Evidence Agent cannot accept gate rail_evidence; the current final-study readiness audit reports blockers.

## Reviewed Inputs

- data/parameters/parameter_evidence_review_packet.csv
- data/parameters/parameter_evidence_source_request_packet.csv
- data/parameters/parameter_source_readiness_manifest.json
- data/parameters/parameter_evidence_priority_manifest.json
- data/parameters/parameter_source_decision_manifest.json
- data/parameters/transfer_evidence_review_manifest.json
- data/parameters/road_evidence_review_packet.csv
- data/road/road_evidence_source_request_packet.csv
- data/road/road_source_readiness_manifest.json
- data/road/road_source_decision_manifest.json
- data/road/road_evidence_priority_manifest.json
- data/parameters/rail_evidence_review_packet.csv
- data/rail/rail_timing_source_request_packet.csv
- data/rail/rail_fetch_readiness_manifest.json
- data/rail/rail_evidence_priority_manifest.json
- data/rail/rail_source_decision_manifest.json
- data/parameters/rail_service_evidence.csv
- data/parameters/rail_station_bindings.csv
- data/parameters/rail_evidence_review_manifest.json
- data/rail/rail_timing_source_request_manifest.json
- data/rail/rail_fetch_readiness_packet.csv
- docs/rail_fetch_readiness_packet.md
- data/rail/rail_evidence_priority_packet.csv
- docs/rail_evidence_priority_packet.md
- data/rail/rail_source_decision_packet.csv
- docs/rail_source_decision_packet.md
- scripts/audit_rail_evidence.py
- scripts/write_rail_evidence_review_packet.py
- scripts/write_rail_timing_source_request_packet.py
- scripts/write_rail_fetch_readiness_packet.py
- scripts/write_rail_evidence_priority_packet.py
- scripts/write_rail_source_decision_packet.py
- scripts/fetch_rail_timetable_cache.py
- scripts/derive_rail_headway_evidence.py
- scripts/derive_rail_service_evidence.py
- scripts/derive_rail_gtfs_evidence.py
- docs/schemas/rail_gtfs_cache_schema.md
- scripts/fetch_rail_shortest_path_cache.py
- scripts/derive_rail_shortest_path_evidence.py
- data/rail/rail_transit_stress_profile_packet.csv
- data/rail/rail_transit_stress_profile_manifest.json
- docs/rail_transit_stress_profile_packet.md
- scripts/write_rail_transit_stress_profile_packet.py
- data/rail/rail_bounded_treatment_audit.json
- docs/rail_bounded_treatment_audit.md
- scripts/audit_rail_bounded_treatments.py

## Evidence And Source Paths

- data/parameters/rail_service_evidence.csv
- data/parameters/rail_station_bindings.csv
- data/parameters/rail_evidence_review_packet.csv
- data/parameters/rail_evidence_review_manifest.json
- data/rail/rail_timing_source_request_packet.csv
- data/rail/rail_timing_source_request_manifest.json
- data/rail/rail_fetch_readiness_packet.csv
- data/rail/rail_fetch_readiness_manifest.json
- docs/rail_fetch_readiness_packet.md
- data/rail/rail_evidence_priority_packet.csv
- data/rail/rail_evidence_priority_manifest.json
- docs/rail_evidence_priority_packet.md
- data/rail/rail_source_decision_packet.csv
- data/rail/rail_source_decision_manifest.json
- docs/rail_source_decision_packet.md
- scripts/audit_rail_evidence.py
- scripts/write_rail_evidence_review_packet.py
- scripts/write_rail_timing_source_request_packet.py
- scripts/write_rail_fetch_readiness_packet.py
- scripts/write_rail_evidence_priority_packet.py
- scripts/write_rail_source_decision_packet.py
- scripts/fetch_rail_timetable_cache.py
- scripts/derive_rail_headway_evidence.py
- scripts/derive_rail_service_evidence.py
- scripts/derive_rail_gtfs_evidence.py
- docs/schemas/rail_gtfs_cache_schema.md
- scripts/fetch_rail_shortest_path_cache.py
- scripts/derive_rail_shortest_path_evidence.py
- data/rail/rail_transit_stress_profile_packet.csv
- data/rail/rail_transit_stress_profile_manifest.json
- docs/rail_transit_stress_profile_packet.md
- scripts/write_rail_transit_stress_profile_packet.py
- data/rail/rail_bounded_treatment_audit.json
- docs/rail_bounded_treatment_audit.md
- scripts/audit_rail_bounded_treatments.py
- data/parameters/parameter_evidence_review_packet.csv
- data/parameters/parameter_source_readiness_packet.csv
- data/parameters/parameter_evidence_priority_packet.csv
- data/parameters/parameter_source_decision_packet.csv
- data/parameters/transfer_evidence_review_packet.csv
- data/parameters/road_evidence_review_packet.csv
- data/road/road_source_readiness_packet.csv
- data/road/road_source_decision_packet.csv
- data/road/road_evidence_priority_packet.csv
- docs/review_packets/cached_osm_input.md
- docs/review_packets/parameter_evidence.md
- docs/review_packets/rail_evidence.md
- data/parameters/parameter_sources.csv
- data/parameters/road_class_overrides_draft.csv
- data/parameters/road_class_overrides.csv
- data/parameters/parameter_acceptance.csv

## Risks

- Road capacity and speed fallbacks are proxy values.
- Rail timing and capacity evidence remains assumption or sensitivity-only in the scaffold.
- Weak core parameters can determine the policy winner.
- rail service evidence: cache timetable, shortest-path, or GTFS-derived records
- rail service evidence: derive headway and travel time from the cached records
- rail fetch readiness: source-backed rail timing evidence remains incomplete until every required timing source is reviewed and retained
- rail fetch readiness: API-key rows require DATA_GO_KR_KEY or reviewed cached API payloads
- rail fetch readiness: reviewed-GTFS row requires a reviewed GTFS input and validator report
- rail fetch readiness: reviewed-static-timetable cache is retained for headway review only; it does not close rail travel-time evidence
- rail fetch readiness: capacity and availability rows still require reviewer-scoped bounded treatment or source-backed evidence
- rail fetch readiness: this packet is readiness evidence only and cannot create rail_service_evidence.csv
- rail evidence priority: source-backed rail timing evidence remains incomplete until API/GTFS/travel-time source paths are reviewed and retained
- rail evidence priority: DATA_GO_KR_KEY, reviewed GTFS input, or reviewed shortest-path cache is absent
- rail evidence priority: capacity and availability treatment still require human/source-backed decisions
- rail source decision: rail source decisions are pending for timetable, shortest-path, GTFS, capacity, and availability requests
- rail source decision: rail timing cache or reviewed GTFS source files remain required for source-backed timing claims
- rail source decision: retained rail capacity and availability assumptions require source-backed updates, sensitivity-only limits, scenario-only limits, or reviewer-scoped bounded treatment
- rail source decision: non-formal source decisions do not close rail evidence, publication, final-study, or formal acceptance gates
- rail source decision: rail_shortest_path_travel_time_request: DATA_GO_KR_KEY is absent and no cached payload is present
- rail source decision: rail_static_gtfs_timing_request: reviewed GTFS file or GTFS Validator report is absent
- rail source decision: rail_timetable_headway_request: DATA_GO_KR_KEY is absent and no cached payload is present
- record reviewed rail source decisions for every row with zero blocking and human-review rows
- non-formal rail source-decision action ledger cannot close rail evidence gate
- rail source-decision action ledger is not formal acceptance evidence
- rail transit stress profile cannot support rail evidence gate
- rail transit stress profile is not publication-ready evidence
- rail transit stress profile cannot mark complete
- rail transit stress profile: rail transit stress profiles are scenario/sensitivity review support only
- rail transit stress profile: capacity and availability profiles require reviewer decisions before final claims
- rail transit stress profile: rail source decision: rail source decisions are pending for timetable, shortest-path, GTFS, capacity, and availability requests
- rail transit stress profile: rail source decision: rail timing cache or reviewed GTFS source files remain required for source-backed timing claims
- rail transit stress profile: rail source decision: retained rail capacity and availability assumptions require source-backed updates, sensitivity-only limits, scenario-only limits, or reviewer-scoped bounded treatment
- rail transit stress profile: rail source decision: non-formal source decisions do not close rail evidence, publication, final-study, or formal acceptance gates
- rail transit stress profile: rail source decision: rail_shortest_path_travel_time_request: DATA_GO_KR_KEY is absent and no cached payload is present
- rail transit stress profile: rail source decision: rail_static_gtfs_timing_request: reviewed GTFS file or GTFS Validator report is absent
- rail transit stress profile: rail source decision: rail_timetable_headway_request: DATA_GO_KR_KEY is absent and no cached payload is present
- 4 rail bounded-treatment warnings remain
- 2 rail bounded-treatment source decisions remain pending

## Required Actions

- Replace weak road, rail, and parameter assumptions with source-backed evidence or explicit accepted overrides.
- Create road_class_overrides.csv and parameter_acceptance.csv only after review.
- rail service evidence: cache timetable, shortest-path, or GTFS-derived records
- rail service evidence: derive headway and travel time from the cached records
- rail fetch readiness: source-backed rail timing evidence remains incomplete until every required timing source is reviewed and retained
- rail fetch readiness: API-key rows require DATA_GO_KR_KEY or reviewed cached API payloads
- rail fetch readiness: reviewed-GTFS row requires a reviewed GTFS input and validator report
- rail fetch readiness: reviewed-static-timetable cache is retained for headway review only; it does not close rail travel-time evidence
- rail fetch readiness: capacity and availability rows still require reviewer-scoped bounded treatment or source-backed evidence
- rail fetch readiness: this packet is readiness evidence only and cannot create rail_service_evidence.csv
- rail evidence priority: source-backed rail timing evidence remains incomplete until API/GTFS/travel-time source paths are reviewed and retained
- rail evidence priority: DATA_GO_KR_KEY, reviewed GTFS input, or reviewed shortest-path cache is absent
- rail evidence priority: capacity and availability treatment still require human/source-backed decisions
- rail source decision: rail source decisions are pending for timetable, shortest-path, GTFS, capacity, and availability requests
- rail source decision: rail timing cache or reviewed GTFS source files remain required for source-backed timing claims
- rail source decision: retained rail capacity and availability assumptions require source-backed updates, sensitivity-only limits, scenario-only limits, or reviewer-scoped bounded treatment
- rail source decision: non-formal source decisions do not close rail evidence, publication, final-study, or formal acceptance gates
- rail source decision: rail_shortest_path_travel_time_request: DATA_GO_KR_KEY is absent and no cached payload is present
- rail source decision: rail_static_gtfs_timing_request: reviewed GTFS file or GTFS Validator report is absent
- rail source decision: rail_timetable_headway_request: DATA_GO_KR_KEY is absent and no cached payload is present
- record reviewed rail source decisions for every row with zero blocking and human-review rows
- non-formal rail source-decision action ledger cannot close rail evidence gate
- rail source-decision action ledger is not formal acceptance evidence
- rail transit stress profile cannot support rail evidence gate
- rail transit stress profile is not publication-ready evidence
- rail transit stress profile cannot mark complete
- rail transit stress profile: rail transit stress profiles are scenario/sensitivity review support only
- rail transit stress profile: capacity and availability profiles require reviewer decisions before final claims
- rail transit stress profile: rail source decision: rail source decisions are pending for timetable, shortest-path, GTFS, capacity, and availability requests
- rail transit stress profile: rail source decision: rail timing cache or reviewed GTFS source files remain required for source-backed timing claims
- rail transit stress profile: rail source decision: retained rail capacity and availability assumptions require source-backed updates, sensitivity-only limits, scenario-only limits, or reviewer-scoped bounded treatment
- rail transit stress profile: rail source decision: non-formal source decisions do not close rail evidence, publication, final-study, or formal acceptance gates
- rail transit stress profile: rail source decision: rail_shortest_path_travel_time_request: DATA_GO_KR_KEY is absent and no cached payload is present
- rail transit stress profile: rail source decision: rail_static_gtfs_timing_request: reviewed GTFS file or GTFS Validator report is absent
- rail transit stress profile: rail source decision: rail_timetable_headway_request: DATA_GO_KR_KEY is absent and no cached payload is present
- 4 rail bounded-treatment warnings remain
- 2 rail bounded-treatment source decisions remain pending

## Formal Acceptance Boundary

To close this final-study gate, create or update the formal acceptance artifact listed in the agent definition. Do not edit this review packet as a substitute for formal acceptance.

Formal acceptance artifacts:

- data/parameters/road_class_overrides.csv
- data/parameters/parameter_acceptance.csv

## Current Final-Study Gate Details

```json
{
  "artifact_present": true,
  "blockers": [
    "rail service evidence: cache timetable, shortest-path, or GTFS-derived records",
    "rail service evidence: derive headway and travel time from the cached records",
    "rail fetch readiness: source-backed rail timing evidence remains incomplete until every required timing source is reviewed and retained",
    "rail fetch readiness: API-key rows require DATA_GO_KR_KEY or reviewed cached API payloads",
    "rail fetch readiness: reviewed-GTFS row requires a reviewed GTFS input and validator report",
    "rail fetch readiness: reviewed-static-timetable cache is retained for headway review only; it does not close rail travel-time evidence",
    "rail fetch readiness: capacity and availability rows still require reviewer-scoped bounded treatment or source-backed evidence",
    "rail fetch readiness: this packet is readiness evidence only and cannot create rail_service_evidence.csv",
    "rail evidence priority: source-backed rail timing evidence remains incomplete until API/GTFS/travel-time source paths are reviewed and retained",
    "rail evidence priority: DATA_GO_KR_KEY, reviewed GTFS input, or reviewed shortest-path cache is absent",
    "rail evidence priority: capacity and availability treatment still require human/source-backed decisions",
    "rail source decision: rail source decisions are pending for timetable, shortest-path, GTFS, capacity, and availability requests",
    "rail source decision: rail timing cache or reviewed GTFS source files remain required for source-backed timing claims",
    "rail source decision: retained rail capacity and availability assumptions require source-backed updates, sensitivity-only limits, scenario-only limits, or reviewer-scoped bounded treatment",
    "rail source decision: non-formal source decisions do not close rail evidence, publication, final-study, or formal acceptance gates",
    "rail source decision: rail_shortest_path_travel_time_request: DATA_GO_KR_KEY is absent and no cached payload is present",
    "rail source decision: rail_static_gtfs_timing_request: reviewed GTFS file or GTFS Validator report is absent",
    "rail source decision: rail_timetable_headway_request: DATA_GO_KR_KEY is absent and no cached payload is present",
    "record reviewed rail source decisions for every row with zero blocking and human-review rows",
    "non-formal rail source-decision action ledger cannot close rail evidence gate",
    "rail source-decision action ledger is not formal acceptance evidence",
    "rail transit stress profile cannot support rail evidence gate",
    "rail transit stress profile is not publication-ready evidence",
    "rail transit stress profile cannot mark complete",
    "rail transit stress profile: rail transit stress profiles are scenario/sensitivity review support only",
    "rail transit stress profile: capacity and availability profiles require reviewer decisions before final claims",
    "rail transit stress profile: rail source decision: rail source decisions are pending for timetable, shortest-path, GTFS, capacity, and availability requests",
    "rail transit stress profile: rail source decision: rail timing cache or reviewed GTFS source files remain required for source-backed timing claims",
    "rail transit stress profile: rail source decision: retained rail capacity and availability assumptions require source-backed updates, sensitivity-only limits, scenario-only limits, or reviewer-scoped bounded treatment",
    "rail transit stress profile: rail source decision: non-formal source decisions do not close rail evidence, publication, final-study, or formal acceptance gates",
    "rail transit stress profile: rail source decision: rail_shortest_path_travel_time_request: DATA_GO_KR_KEY is absent and no cached payload is present",
    "rail transit stress profile: rail source decision: rail_static_gtfs_timing_request: reviewed GTFS file or GTFS Validator report is absent",
    "rail transit stress profile: rail source decision: rail_timetable_headway_request: DATA_GO_KR_KEY is absent and no cached payload is present",
    "4 rail bounded-treatment warnings remain",
    "2 rail bounded-treatment source decisions remain pending"
  ],
  "details": {
    "fetch_readiness_blocking_request_count": 3,
    "fetch_readiness_can_mark_complete": false,
    "fetch_readiness_manifest_present": true,
    "fetch_readiness_publication_ready": false,
    "fetch_readiness_region_ids": [
      "songpa_public_demo"
    ],
    "fetch_readiness_remaining_blockers": [
      "source-backed rail timing evidence remains incomplete until every required timing source is reviewed and retained",
      "API-key rows require DATA_GO_KR_KEY or reviewed cached API payloads",
      "reviewed-GTFS row requires a reviewed GTFS input and validator report",
      "reviewed-static-timetable cache is retained for headway review only; it does not close rail travel-time evidence",
      "capacity and availability rows still require reviewer-scoped bounded treatment or source-backed evidence",
      "this packet is readiness evidence only and cannot create rail_service_evidence.csv"
    ],
    "fetch_readiness_required_external_input_present_count": 3,
    "fetch_readiness_required_external_input_specified_count": 6,
    "fetch_readiness_required_external_input_text_present_count": 6,
    "fetch_readiness_source_url_or_citation_present_count": 6,
    "fetch_readiness_status_counts": {
      "blocked_missing_data_go_kr_key": 2,
      "blocked_missing_reviewed_gtfs_file": 1,
      "needs_human_review_availability_scenario": 1,
      "needs_human_review_capacity_treatment": 1,
      "ready_reviewed_static_timetable_cache_for_derivation_review": 1
    },
    "rail_bounded_treatment_artifacts_present": true,
    "rail_bounded_treatment_audit_present": true,
    "rail_bounded_treatment_can_mark_complete": false,
    "rail_bounded_treatment_can_support_acceptance_gate": false,
    "rail_bounded_treatment_can_support_rail_gate": false,
    "rail_bounded_treatment_integrity_ready": false,
    "rail_bounded_treatment_mismatch_count": 0,
    "rail_bounded_treatment_publication_ready": false,
    "rail_bounded_treatment_unchecked_pending_decision_count": 2,
    "rail_bounded_treatment_warning_count": 4,
    "rail_evidence_priority_artifacts_present": true,
    "rail_evidence_priority_blocking_priority_count": 3,
    "rail_evidence_priority_can_mark_complete": false,
    "rail_evidence_priority_human_review_priority_count": 2,
    "rail_evidence_priority_publication_ready": false,
    "rail_evidence_priority_row_count": 7,
    "rail_evidence_priority_status_counts": {
      "blocked_missing_data_go_kr_key": 2,
      "blocked_missing_reviewed_gtfs_file": 1,
      "needs_human_review_availability_scenario": 1,
      "needs_human_review_capacity_treatment": 1,
      "prerequisite_ready_not_timing_evidence": 1,
      "ready_reviewed_static_timetable_cache_for_derivation_review": 1
    },
    "rail_evidence_priority_timing_closure_candidate_count": 1,
    "rail_source_decision_accepted_source_backed_rail_service_evidence": false,
    "rail_source_decision_action_ledger_completion_scope": "non_formal_source_review_only",
    "rail_source_decision_artifacts_present": true,
    "rail_source_decision_blocking_decision_count": 3,
    "rail_source_decision_can_mark_complete": false,
    "rail_source_decision_can_support_publication_gate": false,
    "rail_source_decision_can_support_rail_gate": false,
    "rail_source_decision_complete": false,
    "rail_source_decision_completed_action_ledger_is_acceptance": false,
    "rail_source_decision_completed_source_decision_count": 0,
    "rail_source_decision_human_review_decision_count": 3,
    "rail_source_decision_manifest_present": true,
    "rail_source_decision_non_formal_action_ledger_scope": true,
    "rail_source_decision_publication_ready": false,
    "rail_source_decision_rail_service_evidence_gate_closure_candidate_count": 0,
    "rail_source_decision_ready": false,
    "rail_source_decision_recorded": false,
    "rail_source_decision_region_ids": [
      "songpa_public_demo"
    ],
    "rail_source_decision_remaining_blockers": [
      "rail source decisions are pending for timetable, shortest-path, GTFS, capacity, and availability requests",
      "rail timing cache or reviewed GTFS source files remain required for source-backed timing claims",
      "retained rail capacity and availability assumptions require source-backed updates, sensitivity-only limits, scenario-only limits, or reviewer-scoped bounded treatment",
      "non-formal source decisions do not close rail evidence, publication, final-study, or formal acceptance gates",
      "rail_shortest_path_travel_time_request: DATA_GO_KR_KEY is absent and no cached payload is present",
      "rail_static_gtfs_timing_request: reviewed GTFS file or GTFS Validator report is absent",
      "rail_timetable_headway_request: DATA_GO_KR_KEY is absent and no cached payload is present"
    ],
    "rail_source_decision_row_count": 6,
    "rail_source_decision_status_counts": {
      "blocked_missing_rail_source_decision": 3,
      "needs_human_review_rail_source_decision": 2,
      "needs_human_review_ready_rail_source_decision": 1
    },
    "rail_source_decision_timing_source_decision_count": 4,
    "rail_transit_stress_profile_artifacts_present": true,
    "rail_transit_stress_profile_can_mark_complete": false,
    "rail_transit_stress_profile_can_support_rail_gate": false,
    "rail_transit_stress_profile_documented": true,
    "rail_transit_stress_profile_manifest_present": true,
    "rail_transit_stress_profile_missing_runtime_hook_count": 0,
    "rail_transit_stress_profile_publication_ready": false,
    "rail_transit_stress_profile_remaining_blockers": [
      "rail transit stress profiles are scenario/sensitivity review support only",
      "capacity and availability profiles require reviewer decisions before final claims",
      "rail source decision: rail source decisions are pending for timetable, shortest-path, GTFS, capacity, and availability requests",
      "rail source decision: rail timing cache or reviewed GTFS source files remain required for source-backed timing claims",
      "rail source decision: retained rail capacity and availability assumptions require source-backed updates, sensitivity-only limits, scenario-only limits, or reviewer-scoped bounded treatment",
      "rail source decision: non-formal source decisions do not close rail evidence, publication, final-study, or formal acceptance gates",
      "rail source decision: rail_shortest_path_travel_time_request: DATA_GO_KR_KEY is absent and no cached payload is present",
      "rail source decision: rail_static_gtfs_timing_request: reviewed GTFS file or GTFS Validator report is absent",
      "rail source decision: rail_timetable_headway_request: DATA_GO_KR_KEY is absent and no cached payload is present"
    ],
    "rail_transit_stress_profile_required_classes_present": true,
    "rail_transit_stress_profile_row_count": 6,
    "rail_transit_stress_profile_supports_rail_gate": false,
    "rail_transit_stress_profile_unresolved_linked_artifact_count": 0,
    "service_publication_ready": false,
    "station_binding_ready": true
  },
  "evidence": [
    "data/parameters/rail_service_evidence.csv",
    "data/parameters/rail_station_bindings.csv",
    "data/parameters/rail_evidence_review_packet.csv",
    "data/parameters/rail_evidence_review_manifest.json",
    "data/rail/rail_timing_source_request_packet.csv",
    "data/rail/rail_timing_source_request_manifest.json",
    "data/rail/rail_fetch_readiness_packet.csv",
    "data/rail/rail_fetch_readiness_manifest.json",
    "docs/rail_fetch_readiness_packet.md",
    "data/rail/rail_evidence_priority_packet.csv",
    "data/rail/rail_evidence_priority_manifest.json",
    "docs/rail_evidence_priority_packet.md",
    "data/rail/rail_source_decision_packet.csv",
    "data/rail/rail_source_decision_manifest.json",
    "docs/rail_source_decision_packet.md",
    "scripts/audit_rail_evidence.py",
    "scripts/write_rail_evidence_review_packet.py",
    "scripts/write_rail_timing_source_request_packet.py",
    "scripts/write_rail_fetch_readiness_packet.py",
    "scripts/write_rail_evidence_priority_packet.py",
    "scripts/write_rail_source_decision_packet.py",
    "scripts/fetch_rail_timetable_cache.py",
    "scripts/derive_rail_headway_evidence.py",
    "scripts/derive_rail_service_evidence.py",
    "scripts/derive_rail_gtfs_evidence.py",
    "docs/schemas/rail_gtfs_cache_schema.md",
    "scripts/fetch_rail_shortest_path_cache.py",
    "scripts/derive_rail_shortest_path_evidence.py",
    "data/rail/rail_transit_stress_profile_packet.csv",
    "data/rail/rail_transit_stress_profile_manifest.json",
    "docs/rail_transit_stress_profile_packet.md",
    "scripts/write_rail_transit_stress_profile_packet.py",
    "data/rail/rail_bounded_treatment_audit.json",
    "docs/rail_bounded_treatment_audit.md",
    "scripts/audit_rail_bounded_treatments.py"
  ],
  "gate_id": "rail_evidence",
  "label": "Rail Evidence",
  "ready": false
}
```
