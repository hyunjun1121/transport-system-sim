# Parameter Evidence Review Packet

Sub-agent records are review aids. They do not replace formal acceptance artifacts, source-backed reviewer decisions, calibrated validation, or operational routing approval.

- Gate ID: `parameter_evidence`
- Agent: `Road / Rail / Parameter Evidence Agent`
- Status: `blocked`
- Can mark complete: `false`
- Generated at: `2026-05-04T11:33:48+00:00`

## Decision

Road / Rail / Parameter Evidence Agent cannot accept gate parameter_evidence; the current final-study readiness audit reports blockers.

## Reviewed Inputs

- data/parameters/parameter_evidence_review_packet.csv
- data/parameters/parameter_evidence_source_request_packet.csv
- data/parameters/road_evidence_review_packet.csv
- data/parameters/rail_evidence_review_packet.csv
- data/rail/rail_timing_source_request_packet.csv
- data/parameters/parameter_sources.csv
- data/parameters/parameter_evidence_review_manifest.json
- data/parameters/parameter_evidence_source_request_manifest.json
- scripts/audit_parameter_evidence.py
- scripts/write_parameter_review_packet.py
- scripts/write_parameter_evidence_source_request_packet.py

## Evidence And Source Paths

- data/parameters/parameter_sources.csv
- data/parameters/parameter_evidence_review_packet.csv
- data/parameters/parameter_evidence_review_manifest.json
- data/parameters/parameter_evidence_source_request_packet.csv
- data/parameters/parameter_evidence_source_request_manifest.json
- scripts/audit_parameter_evidence.py
- scripts/write_parameter_review_packet.py
- scripts/write_parameter_evidence_source_request_packet.py
- data/parameters/road_evidence_review_packet.csv
- data/parameters/rail_evidence_review_packet.csv
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

## Required Actions

- Replace weak road, rail, and parameter assumptions with source-backed evidence or explicit accepted overrides.
- Create road_class_overrides.csv and parameter_acceptance.csv only after review.
- justify demand scale, arrival process, time horizon, and censoring penalties with planning assumptions or sensitivity-bound evidence
- replace scenario-only disruption probabilities and degradation rules with public hazard, incident, literature, or expert-reviewed evidence
- replace generic fleet and vehicle-capacity assumptions with agency, planning, literature, or accepted scenario evidence
- derive rail headway and travel time from cached GTFS, timetable, operator, or agency records, and keep rail capacity source-backed or explicitly sensitivity-only
- strengthen road speed, capacity, and background traffic values with public speed limits, traffic counts, or benchmark-calibrated routing
- support transfer delays with station-layout evidence, observed ranges, or literature rather than generic fixed delays

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
    "support transfer delays with station-layout evidence, observed ranges, or literature rather than generic fixed delays"
  ],
  "details": {},
  "evidence": [
    "data/parameters/parameter_sources.csv",
    "data/parameters/parameter_evidence_review_packet.csv",
    "data/parameters/parameter_evidence_review_manifest.json",
    "data/parameters/parameter_evidence_source_request_packet.csv",
    "data/parameters/parameter_evidence_source_request_manifest.json",
    "scripts/audit_parameter_evidence.py",
    "scripts/write_parameter_review_packet.py",
    "scripts/write_parameter_evidence_source_request_packet.py"
  ],
  "gate_id": "parameter_evidence",
  "label": "Parameter Evidence",
  "ready": false
}
```
