# Rail Evidence Review Packet

Sub-agent records are review aids. They do not replace formal acceptance artifacts, source-backed reviewer decisions, calibrated validation, or operational routing approval.

- Gate ID: `rail_evidence`
- Agent: `Road / Rail / Parameter Evidence Agent`
- Status: `blocked`
- Can mark complete: `false`
- Generated at: `2026-05-09T03:27:03+00:00`

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
- rail fetch readiness: rail timing cache files are absent unless source_cache_present is true
- rail fetch readiness: API-key and reviewed-GTFS rows require external reviewer-provided inputs
- rail fetch readiness: this packet is readiness evidence only and cannot create rail_service_evidence.csv
- rail evidence priority: rail timing cache files are absent
- rail evidence priority: DATA_GO_KR_KEY or reviewed GTFS input is absent
- rail evidence priority: capacity and availability treatment still require human/source-backed decisions
- rail source decision: rail source decisions are pending for timetable, shortest-path, GTFS, capacity, and availability requests
- rail source decision: rail timing cache or reviewed GTFS source files are absent for timing requests
- rail source decision: retained rail capacity and availability assumptions require source-backed updates, sensitivity-only limits, scenario-only limits, or explicit acceptance
- rail source decision: rail_shortest_path_travel_time_request: DATA_GO_KR_KEY is absent and no cached payload is present
- rail source decision: rail_static_gtfs_timing_request: reviewed GTFS file is absent
- rail source decision: rail_timetable_headway_request: DATA_GO_KR_KEY is absent and no cached payload is present

## Required Actions

- Replace weak road, rail, and parameter assumptions with source-backed evidence or explicit accepted overrides.
- Create road_class_overrides.csv and parameter_acceptance.csv only after review.
- rail service evidence: cache timetable, shortest-path, or GTFS-derived records
- rail service evidence: derive headway and travel time from the cached records
- rail fetch readiness: rail timing cache files are absent unless source_cache_present is true
- rail fetch readiness: API-key and reviewed-GTFS rows require external reviewer-provided inputs
- rail fetch readiness: this packet is readiness evidence only and cannot create rail_service_evidence.csv
- rail evidence priority: rail timing cache files are absent
- rail evidence priority: DATA_GO_KR_KEY or reviewed GTFS input is absent
- rail evidence priority: capacity and availability treatment still require human/source-backed decisions
- rail source decision: rail source decisions are pending for timetable, shortest-path, GTFS, capacity, and availability requests
- rail source decision: rail timing cache or reviewed GTFS source files are absent for timing requests
- rail source decision: retained rail capacity and availability assumptions require source-backed updates, sensitivity-only limits, scenario-only limits, or explicit acceptance
- rail source decision: rail_shortest_path_travel_time_request: DATA_GO_KR_KEY is absent and no cached payload is present
- rail source decision: rail_static_gtfs_timing_request: reviewed GTFS file is absent
- rail source decision: rail_timetable_headway_request: DATA_GO_KR_KEY is absent and no cached payload is present

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
    "rail fetch readiness: rail timing cache files are absent unless source_cache_present is true",
    "rail fetch readiness: API-key and reviewed-GTFS rows require external reviewer-provided inputs",
    "rail fetch readiness: this packet is readiness evidence only and cannot create rail_service_evidence.csv",
    "rail evidence priority: rail timing cache files are absent",
    "rail evidence priority: DATA_GO_KR_KEY or reviewed GTFS input is absent",
    "rail evidence priority: capacity and availability treatment still require human/source-backed decisions",
    "rail source decision: rail source decisions are pending for timetable, shortest-path, GTFS, capacity, and availability requests",
    "rail source decision: rail timing cache or reviewed GTFS source files are absent for timing requests",
    "rail source decision: retained rail capacity and availability assumptions require source-backed updates, sensitivity-only limits, scenario-only limits, or explicit acceptance",
    "rail source decision: rail_shortest_path_travel_time_request: DATA_GO_KR_KEY is absent and no cached payload is present",
    "rail source decision: rail_static_gtfs_timing_request: reviewed GTFS file is absent",
    "rail source decision: rail_timetable_headway_request: DATA_GO_KR_KEY is absent and no cached payload is present"
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
      "rail timing cache files are absent unless source_cache_present is true",
      "API-key and reviewed-GTFS rows require external reviewer-provided inputs",
      "this packet is readiness evidence only and cannot create rail_service_evidence.csv"
    ],
    "fetch_readiness_required_external_input_present_count": 5,
    "fetch_readiness_source_url_or_citation_present_count": 5,
    "fetch_readiness_status_counts": {
      "blocked_missing_data_go_kr_key": 2,
      "blocked_missing_reviewed_gtfs_file": 1,
      "needs_human_review_availability_scenario": 1,
      "needs_human_review_capacity_treatment": 1
    },
    "rail_evidence_priority_artifacts_present": true,
    "rail_evidence_priority_blocking_priority_count": 3,
    "rail_evidence_priority_can_mark_complete": false,
    "rail_evidence_priority_human_review_priority_count": 2,
    "rail_evidence_priority_publication_ready": false,
    "rail_evidence_priority_row_count": 6,
    "rail_evidence_priority_status_counts": {
      "blocked_missing_data_go_kr_key": 2,
      "blocked_missing_reviewed_gtfs_file": 1,
      "needs_human_review_availability_scenario": 1,
      "needs_human_review_capacity_treatment": 1,
      "prerequisite_ready_not_timing_evidence": 1
    },
    "rail_evidence_priority_timing_closure_candidate_count": 1,
    "rail_source_decision_artifacts_present": true,
    "rail_source_decision_blocking_decision_count": 3,
    "rail_source_decision_can_mark_complete": false,
    "rail_source_decision_human_review_decision_count": 2,
    "rail_source_decision_manifest_present": true,
    "rail_source_decision_publication_ready": false,
    "rail_source_decision_recorded": false,
    "rail_source_decision_region_ids": [
      "songpa_public_demo"
    ],
    "rail_source_decision_remaining_blockers": [
      "rail source decisions are pending for timetable, shortest-path, GTFS, capacity, and availability requests",
      "rail timing cache or reviewed GTFS source files are absent for timing requests",
      "retained rail capacity and availability assumptions require source-backed updates, sensitivity-only limits, scenario-only limits, or explicit acceptance",
      "rail_shortest_path_travel_time_request: DATA_GO_KR_KEY is absent and no cached payload is present",
      "rail_static_gtfs_timing_request: reviewed GTFS file is absent",
      "rail_timetable_headway_request: DATA_GO_KR_KEY is absent and no cached payload is present"
    ],
    "rail_source_decision_row_count": 5,
    "rail_source_decision_status_counts": {
      "blocked_missing_rail_source_decision": 3,
      "needs_human_review_rail_source_decision": 2
    },
    "rail_source_decision_timing_source_decision_count": 3,
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
    "scripts/derive_rail_shortest_path_evidence.py"
  ],
  "gate_id": "rail_evidence",
  "label": "Rail Evidence",
  "ready": false
}
```
