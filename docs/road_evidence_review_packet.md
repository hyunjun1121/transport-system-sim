# Road Evidence Review Packet

## Scope

`data/parameters/road_evidence_review_packet.csv` is a road-class review
worksheet for the current cached OSM/GraphML pilot road input. It consolidates
the road-class diagnostics, sparse cached OSM `maxspeed` evidence, cached OSM
`lanes` evidence, and the draft road-class override worksheet.

The packet is not an accepted road-calibration table, not an applied
road-class override table, not traffic assignment validation, and not
operational routing evidence.

## Generated Artifacts

| Artifact | Role | Current Scope |
| --- | --- | --- |
| `data/parameters/road_evidence_review_packet.csv` | 10-row road-class review worksheet | review support only |
| `data/parameters/road_evidence_review_manifest.json` | Summary of weak rows, evidence status counts, priorities, and claim boundary | review support only |
| `scripts/write_road_evidence_review_packet.py` | Regenerates the worksheet and manifest from cached road inputs | deterministic scaffold command |
| `src/realworld/road_evidence_review_packet.py` | Library implementation for row construction and manifest writing | project-owned code |
| `data/road/road_evidence_source_request_packet.csv` | Follow-on source-request worksheet for collecting road evidence inputs | request support only |
| `scripts/write_road_evidence_source_request_packet.py` | Regenerates the source-request worksheet and manifest | deterministic scaffold command |

## Current Status

The current packet has 10 routeable road-class rows. All rows remain weak for
final-study claims because cached lane-count evidence and base-disruption
probability evidence are absent, and the draft override worksheet still uses
expert-assumption source classes.

The strongest current use is prioritization. Reviewers should use the packet
to decide which road classes should receive source-backed speed, capacity, and
base-disruption evidence first, and which values can remain explicit
sensitivity-only or accepted scenario assumptions.

## Regeneration

```powershell
.\.venv\Scripts\python scripts\write_road_evidence_review_packet.py
.\.venv\Scripts\python scripts\write_road_evidence_source_request_packet.py
.\.venv\Scripts\python scripts\audit_road_evidence.py
.\.venv\Scripts\python scripts\audit_road_evidence_diagnostics.py
.\.venv\Scripts\python scripts\audit_road_overrides.py
.\.venv\Scripts\python scripts\audit_publication_readiness.py
.\.venv\Scripts\python scripts\audit_final_study_readiness.py
```

## Claim Boundary

Do not cite the packet as calibrated road evidence. It documents road-input
evidence gaps and review priorities. Final-study road claims remain blocked
until weak values are replaced with reviewed evidence, moved into
`data/parameters/road_class_overrides.csv`, applied to accepted pilot outputs,
and recorded inside the relevant final-study acceptance gates.
