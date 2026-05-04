# Cached OSM Input Review Packet

Sub-agent records are review aids. They do not replace formal acceptance artifacts, source-backed reviewer decisions, calibrated validation, or operational routing approval.

- Gate ID: `cached_osm_input`
- Agent: `Road / Rail / Parameter Evidence Agent`
- Status: `blocked`
- Can mark complete: `false`
- Generated at: `2026-05-04T13:32:58+00:00`

## Decision

Road / Rail / Parameter Evidence Agent cannot accept gate cached_osm_input; the current final-study readiness audit reports blockers.

## Reviewed Inputs

- data/parameters/parameter_evidence_review_packet.csv
- data/parameters/parameter_evidence_source_request_packet.csv
- data/parameters/road_evidence_review_packet.csv
- data/parameters/rail_evidence_review_packet.csv
- data/rail/rail_timing_source_request_packet.csv
- data/cache/pilot_region_road.graphml
- data/cache/pilot_region_road_manifest.json
- scripts/audit_road_evidence.py
- scripts/audit_road_evidence_diagnostics.py
- data/parameters/road_speed_evidence_candidates.csv
- data/parameters/road_capacity_evidence_candidates.csv
- data/parameters/road_evidence_review_manifest.json
- data/road/road_evidence_source_request_packet.csv
- data/road/road_evidence_source_request_manifest.json
- data/road/road_source_readiness_packet.csv
- data/road/road_source_readiness_manifest.json
- docs/road_source_readiness_packet.md
- scripts/write_road_speed_evidence.py
- scripts/write_road_capacity_evidence.py
- scripts/write_road_evidence_review_packet.py
- scripts/write_road_evidence_source_request_packet.py
- scripts/write_road_source_readiness_packet.py
- data/parameters/road_class_overrides_draft.csv
- scripts/write_road_class_override_template.py
- scripts/audit_road_overrides.py

## Evidence And Source Paths

- data/cache/pilot_region_road.graphml
- data/cache/pilot_region_road_manifest.json
- scripts/audit_road_evidence.py
- scripts/audit_road_evidence_diagnostics.py
- data/parameters/road_speed_evidence_candidates.csv
- data/parameters/road_capacity_evidence_candidates.csv
- data/parameters/road_evidence_review_packet.csv
- data/parameters/road_evidence_review_manifest.json
- data/road/road_evidence_source_request_packet.csv
- data/road/road_evidence_source_request_manifest.json
- data/road/road_source_readiness_packet.csv
- data/road/road_source_readiness_manifest.json
- docs/road_source_readiness_packet.md
- scripts/write_road_speed_evidence.py
- scripts/write_road_capacity_evidence.py
- scripts/write_road_evidence_review_packet.py
- scripts/write_road_evidence_source_request_packet.py
- scripts/write_road_source_readiness_packet.py
- data/parameters/road_class_overrides_draft.csv
- scripts/write_road_class_override_template.py
- scripts/audit_road_overrides.py
- data/parameters/parameter_evidence_review_packet.csv
- data/parameters/rail_evidence_review_packet.csv
- docs/review_packets/cached_osm_input.md
- docs/review_packets/parameter_evidence.md
- docs/review_packets/rail_evidence.md
- data/parameters/parameter_sources.csv
- data/parameters/rail_service_evidence.csv
- data/parameters/rail_station_bindings.csv
- data/parameters/road_class_overrides.csv
- data/parameters/parameter_acceptance.csv

## Risks

- Road capacity and speed fallbacks are proxy values.
- Rail timing and capacity evidence remains assumption or sensitivity-only in the scaffold.
- Weak core parameters can determine the policy winner.
- road input evidence: review OSM maxspeed coverage and replace fallback free-flow speeds where final claims require calibration
- road input evidence: replace road-class capacity proxies with traffic counts, agency capacity references, or benchmark-calibrated values
- road input evidence: replace road-class base disruption probabilities with hazard, incident, or accepted scenario evidence
- road input evidence: treat this as road-input evidence only; route plausibility and traffic validation remain separate gates
- road override evidence: replace the draft road-class override worksheet with a reviewed road_class_overrides.csv table containing source-backed speed, capacity, and base-disruption evidence
- road override evidence: apply the reviewed overrides when adapting the pilot graph if final claims require calibrated road inputs
- road override application: reviewed road-class override table is absent

## Required Actions

- Replace weak road, rail, and parameter assumptions with source-backed evidence or explicit accepted overrides.
- Create road_class_overrides.csv and parameter_acceptance.csv only after review.
- road input evidence: review OSM maxspeed coverage and replace fallback free-flow speeds where final claims require calibration
- road input evidence: replace road-class capacity proxies with traffic counts, agency capacity references, or benchmark-calibrated values
- road input evidence: replace road-class base disruption probabilities with hazard, incident, or accepted scenario evidence
- road input evidence: treat this as road-input evidence only; route plausibility and traffic validation remain separate gates
- road override evidence: replace the draft road-class override worksheet with a reviewed road_class_overrides.csv table containing source-backed speed, capacity, and base-disruption evidence
- road override evidence: apply the reviewed overrides when adapting the pilot graph if final claims require calibrated road inputs
- road override application: reviewed road-class override table is absent

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
    "road input evidence: review OSM maxspeed coverage and replace fallback free-flow speeds where final claims require calibration",
    "road input evidence: replace road-class capacity proxies with traffic counts, agency capacity references, or benchmark-calibrated values",
    "road input evidence: replace road-class base disruption probabilities with hazard, incident, or accepted scenario evidence",
    "road input evidence: treat this as road-input evidence only; route plausibility and traffic validation remain separate gates",
    "road override evidence: replace the draft road-class override worksheet with a reviewed road_class_overrides.csv table containing source-backed speed, capacity, and base-disruption evidence",
    "road override evidence: apply the reviewed overrides when adapting the pilot graph if final claims require calibrated road inputs",
    "road override application: reviewed road-class override table is absent"
  ],
  "details": {
    "edge_count": 28947,
    "override_application_ready": false,
    "road_diagnostics_ready": true,
    "road_diagnostics_top_review_candidates": [
      "residential",
      "tertiary",
      "secondary",
      "primary",
      "trunk"
    ],
    "road_override_draft_row_count": 10,
    "road_override_draft_table_present": true,
    "road_publication_ready": false,
    "routeable_edge_count": 9140,
    "source_readiness_blocking_request_count": 2,
    "source_readiness_can_mark_complete": false,
    "source_readiness_human_review_request_count": 3,
    "source_readiness_manifest_present": true,
    "source_readiness_publication_ready": false,
    "source_readiness_status_counts": {
      "blocked_missing_capacity_source": 1,
      "blocked_missing_reviewed_road_class_overrides": 1,
      "needs_human_review_benchmark_strategy": 1,
      "needs_human_review_disruption_scenario": 1,
      "needs_human_review_sparse_speed_candidates": 1
    }
  },
  "evidence": [
    "data/cache/pilot_region_road.graphml",
    "data/cache/pilot_region_road_manifest.json",
    "scripts/audit_road_evidence.py",
    "scripts/audit_road_evidence_diagnostics.py",
    "data/parameters/road_speed_evidence_candidates.csv",
    "data/parameters/road_capacity_evidence_candidates.csv",
    "data/parameters/road_evidence_review_packet.csv",
    "data/parameters/road_evidence_review_manifest.json",
    "data/road/road_evidence_source_request_packet.csv",
    "data/road/road_evidence_source_request_manifest.json",
    "data/road/road_source_readiness_packet.csv",
    "data/road/road_source_readiness_manifest.json",
    "docs/road_source_readiness_packet.md",
    "scripts/write_road_speed_evidence.py",
    "scripts/write_road_capacity_evidence.py",
    "scripts/write_road_evidence_review_packet.py",
    "scripts/write_road_evidence_source_request_packet.py",
    "scripts/write_road_source_readiness_packet.py",
    "data/parameters/road_class_overrides_draft.csv",
    "scripts/write_road_class_override_template.py",
    "scripts/audit_road_overrides.py"
  ],
  "gate_id": "cached_osm_input",
  "label": "Cached OSM Input",
  "ready": false
}
```
