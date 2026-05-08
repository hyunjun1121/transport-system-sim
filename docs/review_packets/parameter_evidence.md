# Parameter Evidence Review Packet

Sub-agent records are review aids. They do not replace formal acceptance artifacts, source-backed reviewer decisions, calibrated validation, or operational routing approval.

- Gate ID: `parameter_evidence`
- Agent: `Road / Rail / Parameter Evidence Agent`
- Status: `blocked`
- Can mark complete: `false`
- Generated at: `2026-05-08T22:27:49+00:00`

## Decision

Road / Rail / Parameter Evidence Agent cannot accept gate parameter_evidence; the current final-study readiness audit reports blockers.

## Reviewed Inputs

- data/parameters/parameter_evidence_review_packet.csv
- data/parameters/parameter_evidence_source_request_packet.csv
- data/parameters/parameter_source_readiness_manifest.json
- data/parameters/parameter_evidence_priority_manifest.json
- data/parameters/parameter_source_decision_manifest.json
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
- data/parameters/parameter_sources.csv
- data/parameters/parameter_evidence_review_manifest.json
- data/parameters/parameter_evidence_source_request_manifest.json
- data/parameters/parameter_source_readiness_packet.csv
- docs/parameter_source_readiness_packet.md
- data/parameters/parameter_evidence_priority_packet.csv
- docs/parameter_evidence_priority_packet.md
- data/parameters/parameter_source_decision_packet.csv
- docs/parameter_source_decision_packet.md
- scripts/audit_parameter_evidence.py
- scripts/write_parameter_review_packet.py
- scripts/write_parameter_evidence_source_request_packet.py
- scripts/write_parameter_source_readiness_packet.py
- scripts/write_parameter_evidence_priority_packet.py
- scripts/write_parameter_source_decision_packet.py

## Evidence And Source Paths

- data/parameters/parameter_sources.csv
- data/parameters/parameter_evidence_review_packet.csv
- data/parameters/parameter_evidence_review_manifest.json
- data/parameters/parameter_evidence_source_request_packet.csv
- data/parameters/parameter_evidence_source_request_manifest.json
- data/parameters/parameter_source_readiness_packet.csv
- data/parameters/parameter_source_readiness_manifest.json
- docs/parameter_source_readiness_packet.md
- data/parameters/parameter_evidence_priority_packet.csv
- data/parameters/parameter_evidence_priority_manifest.json
- docs/parameter_evidence_priority_packet.md
- data/parameters/parameter_source_decision_packet.csv
- data/parameters/parameter_source_decision_manifest.json
- docs/parameter_source_decision_packet.md
- scripts/audit_parameter_evidence.py
- scripts/write_parameter_review_packet.py
- scripts/write_parameter_evidence_source_request_packet.py
- scripts/write_parameter_source_readiness_packet.py
- scripts/write_parameter_evidence_priority_packet.py
- scripts/write_parameter_source_decision_packet.py
- data/parameters/road_evidence_review_packet.csv
- data/road/road_source_readiness_packet.csv
- data/road/road_source_decision_packet.csv
- data/road/road_evidence_priority_packet.csv
- data/parameters/rail_evidence_review_packet.csv
- data/rail/rail_fetch_readiness_packet.csv
- data/rail/rail_evidence_priority_packet.csv
- data/rail/rail_source_decision_packet.csv
- docs/review_packets/cached_osm_input.md
- docs/review_packets/parameter_evidence.md
- docs/review_packets/rail_evidence.md
- data/parameters/road_class_overrides_draft.csv
- data/parameters/rail_service_evidence.csv
- data/parameters/rail_station_bindings.csv
- data/parameters/road_class_overrides.csv
- data/parameters/parameter_acceptance.csv

## Risks

- Road capacity and speed fallbacks are proxy values.
- Rail timing and capacity evidence remains assumption or sensitivity-only in the scaffold.
- Weak core parameters can determine the policy winner.
- justify demand scale, arrival process, time horizon, and censoring penalties with planning assumptions or sensitivity-bound evidence
- replace scenario-only disruption probabilities and degradation rules with public hazard, incident, literature, or expert-reviewed evidence
- replace generic fleet and vehicle-capacity assumptions with agency, planning, literature, or accepted scenario evidence
- derive rail headway and travel time from cached GTFS, timetable, operator, or agency records, and keep rail capacity source-backed or explicitly sensitivity-only
- strengthen road speed, capacity, and background traffic values with public speed limits, traffic counts, or benchmark-calibrated routing
- support transfer delays with station-layout evidence, observed ranges, or literature rather than generic fixed delays
- parameter source readiness: all rows require human review or external source decisions before final claims
- parameter source readiness: this packet is readiness evidence only and cannot create accepted parameter values
- parameter source readiness: parameter_acceptance.csv remains separate and absent unless reviewers accept weak assumptions
- parameter evidence priority: transfer-delay source evidence is absent
- parameter evidence priority: high-priority disruption and traffic/BPR rows still require human/source-backed decisions
- parameter evidence priority: medium-priority demand, fleet, and dispatch rows remain scenario assumptions
- parameter evidence priority: parameter_acceptance.csv remains absent unless reviewers accept retained weak assumptions
- parameter source decision: formal parameter acceptance table is absent
- parameter source decision: parameter source decisions are pending for weak parameter groups
- parameter source decision: retained weak assumptions require source-backed updates, sensitivity-only limits, or explicit weak-parameter acceptance
- parameter source decision: transfer_delay_source_request: no station-layout, observed transfer, or pedestrian-flow source artifact is present

## Required Actions

- Replace weak road, rail, and parameter assumptions with source-backed evidence or explicit accepted overrides.
- Create road_class_overrides.csv and parameter_acceptance.csv only after review.
- justify demand scale, arrival process, time horizon, and censoring penalties with planning assumptions or sensitivity-bound evidence
- replace scenario-only disruption probabilities and degradation rules with public hazard, incident, literature, or expert-reviewed evidence
- replace generic fleet and vehicle-capacity assumptions with agency, planning, literature, or accepted scenario evidence
- derive rail headway and travel time from cached GTFS, timetable, operator, or agency records, and keep rail capacity source-backed or explicitly sensitivity-only
- strengthen road speed, capacity, and background traffic values with public speed limits, traffic counts, or benchmark-calibrated routing
- support transfer delays with station-layout evidence, observed ranges, or literature rather than generic fixed delays
- parameter source readiness: all rows require human review or external source decisions before final claims
- parameter source readiness: this packet is readiness evidence only and cannot create accepted parameter values
- parameter source readiness: parameter_acceptance.csv remains separate and absent unless reviewers accept weak assumptions
- parameter evidence priority: transfer-delay source evidence is absent
- parameter evidence priority: high-priority disruption and traffic/BPR rows still require human/source-backed decisions
- parameter evidence priority: medium-priority demand, fleet, and dispatch rows remain scenario assumptions
- parameter evidence priority: parameter_acceptance.csv remains absent unless reviewers accept retained weak assumptions
- parameter source decision: formal parameter acceptance table is absent
- parameter source decision: parameter source decisions are pending for weak parameter groups
- parameter source decision: retained weak assumptions require source-backed updates, sensitivity-only limits, or explicit weak-parameter acceptance
- parameter source decision: transfer_delay_source_request: no station-layout, observed transfer, or pedestrian-flow source artifact is present

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
    "justify demand scale, arrival process, time horizon, and censoring penalties with planning assumptions or sensitivity-bound evidence",
    "replace scenario-only disruption probabilities and degradation rules with public hazard, incident, literature, or expert-reviewed evidence",
    "replace generic fleet and vehicle-capacity assumptions with agency, planning, literature, or accepted scenario evidence",
    "derive rail headway and travel time from cached GTFS, timetable, operator, or agency records, and keep rail capacity source-backed or explicitly sensitivity-only",
    "strengthen road speed, capacity, and background traffic values with public speed limits, traffic counts, or benchmark-calibrated routing",
    "support transfer delays with station-layout evidence, observed ranges, or literature rather than generic fixed delays",
    "parameter source readiness: all rows require human review or external source decisions before final claims",
    "parameter source readiness: this packet is readiness evidence only and cannot create accepted parameter values",
    "parameter source readiness: parameter_acceptance.csv remains separate and absent unless reviewers accept weak assumptions",
    "parameter evidence priority: transfer-delay source evidence is absent",
    "parameter evidence priority: high-priority disruption and traffic/BPR rows still require human/source-backed decisions",
    "parameter evidence priority: medium-priority demand, fleet, and dispatch rows remain scenario assumptions",
    "parameter evidence priority: parameter_acceptance.csv remains absent unless reviewers accept retained weak assumptions",
    "parameter source decision: formal parameter acceptance table is absent",
    "parameter source decision: parameter source decisions are pending for weak parameter groups",
    "parameter source decision: retained weak assumptions require source-backed updates, sensitivity-only limits, or explicit weak-parameter acceptance",
    "parameter source decision: transfer_delay_source_request: no station-layout, observed transfer, or pedestrian-flow source artifact is present"
  ],
  "details": {
    "parameter_evidence_priority_artifacts_present": true,
    "parameter_evidence_priority_blocking_priority_count": 1,
    "parameter_evidence_priority_can_mark_complete": false,
    "parameter_evidence_priority_high_priority_parameter_count": 6,
    "parameter_evidence_priority_human_review_priority_count": 5,
    "parameter_evidence_priority_medium_priority_parameter_count": 14,
    "parameter_evidence_priority_publication_ready": false,
    "parameter_evidence_priority_row_count": 6,
    "parameter_evidence_priority_status_counts": {
      "blocked_missing_parameter_source": 1,
      "needs_human_review_high_priority_parameter_source": 2,
      "needs_human_review_medium_priority_parameter_source": 3
    },
    "parameter_publication_ready": false,
    "parameter_source_decision_artifacts_present": true,
    "parameter_source_decision_blocking_decision_count": 1,
    "parameter_source_decision_can_mark_complete": false,
    "parameter_source_decision_human_review_decision_count": 5,
    "parameter_source_decision_publication_ready": false,
    "parameter_source_decision_recorded": false,
    "parameter_source_decision_row_count": 6,
    "parameter_source_decision_status_counts": {
      "blocked_missing_parameter_source_decision": 1,
      "needs_human_review_parameter_source_decision": 5
    },
    "source_readiness_blocking_request_count": 1,
    "source_readiness_can_mark_complete": false,
    "source_readiness_human_review_request_count": 5,
    "source_readiness_manifest_present": true,
    "source_readiness_publication_ready": false,
    "source_readiness_region_ids": [
      "songpa_public_demo"
    ],
    "source_readiness_remaining_blockers": [
      "all rows require human review or external source decisions before final claims",
      "this packet is readiness evidence only and cannot create accepted parameter values",
      "parameter_acceptance.csv remains separate and absent unless reviewers accept weak assumptions"
    ],
    "source_readiness_required_external_input_present_count": 6,
    "source_readiness_source_url_or_citation_present_count": 6,
    "source_readiness_status_counts": {
      "blocked_missing_transfer_source": 1,
      "needs_human_review_demand_scenario": 1,
      "needs_human_review_dispatch_policy": 1,
      "needs_human_review_disruption_parameter_scenario": 1,
      "needs_human_review_fleet_package": 1,
      "needs_human_review_traffic_bpr_with_benchmark_snapshot": 1
    }
  },
  "evidence": [
    "data/parameters/parameter_sources.csv",
    "data/parameters/parameter_evidence_review_packet.csv",
    "data/parameters/parameter_evidence_review_manifest.json",
    "data/parameters/parameter_evidence_source_request_packet.csv",
    "data/parameters/parameter_evidence_source_request_manifest.json",
    "data/parameters/parameter_source_readiness_packet.csv",
    "data/parameters/parameter_source_readiness_manifest.json",
    "docs/parameter_source_readiness_packet.md",
    "data/parameters/parameter_evidence_priority_packet.csv",
    "data/parameters/parameter_evidence_priority_manifest.json",
    "docs/parameter_evidence_priority_packet.md",
    "data/parameters/parameter_source_decision_packet.csv",
    "data/parameters/parameter_source_decision_manifest.json",
    "docs/parameter_source_decision_packet.md",
    "scripts/audit_parameter_evidence.py",
    "scripts/write_parameter_review_packet.py",
    "scripts/write_parameter_evidence_source_request_packet.py",
    "scripts/write_parameter_source_readiness_packet.py",
    "scripts/write_parameter_evidence_priority_packet.py",
    "scripts/write_parameter_source_decision_packet.py"
  ],
  "gate_id": "parameter_evidence",
  "label": "Parameter Evidence",
  "ready": false
}
```
