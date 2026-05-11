# Parameter Evidence Review Packet

> Current project status (2026-05-08): `final_study_ready=false`. Ready gates are `3/15` (`real_input_smoke`, `structured_disruptions`, `policy_alternatives`), blocked gates are `12/15`, and formal acceptance is `0/12` ready. This document is current-state or review support only; it does not create formal approval, calibrated real-world results, or operational routing guidance.


## Scope

`data/parameters/parameter_evidence_review_packet.csv` is a reviewer worksheet
for the current core-parameter evidence audit. It is not an accepted
calibration table, not an operational input approval, and not a
publication-readiness record.

The packet exists to make the next evidence work explicit: for each core
parameter, it records the parameter group, current evidence category, strongest
source class, review priority, source tables, candidate upgrade artifacts, and
the conservative claim boundary.

## Generated Artifacts

| Artifact | Role | Current Scope |
| --- | --- | --- |
| `data/parameters/parameter_evidence_review_packet.csv` | 29-row core-parameter review worksheet | review support only |
| `data/parameters/parameter_evidence_review_manifest.json` | Summary of weak rows, priorities, groups, and claim boundary | review support only |
| `data/parameters/parameter_evidence_source_request_packet.csv` | 7-row source-request worksheet for cross-cutting weak-parameter evidence collection, including the rail parameter cross-reference row | request support only |
| `data/parameters/parameter_evidence_source_request_manifest.json` | Summary of covered parameters and non-acceptance claim boundary | request support only |
| `scripts/write_parameter_review_packet.py` | Regenerates the worksheet and manifest from shipped parameter tables | deterministic scaffold command |
| `scripts/write_parameter_evidence_source_request_packet.py` | Regenerates the source-request worksheet and manifest | deterministic scaffold command |
| `src/realworld/parameter_review_packet.py` | Library implementation for row construction and manifest writing | project-owned code |

## Current Status

The current packet has 29 core-parameter rows. It reports 25 rows as weak for
final-study claims, grouped across road, disruption, fleet, rail, transfer, and
demand/time/censoring inputs.

The strongest current use is prioritization. Reviewers should use the packet to
decide which parameters should be replaced with public-data, literature,
agency/timetable, or benchmark-supported values, and which parameters can remain
as explicit sensitivity-only or accepted scenario assumptions.

## Regeneration

```powershell
.\.venv\Scripts\python scripts\write_parameter_review_packet.py
.\.venv\Scripts\python scripts\write_parameter_evidence_source_request_packet.py
.\.venv\Scripts\python scripts\audit_parameter_evidence.py
.\.venv\Scripts\python scripts\audit_publication_readiness.py
.\.venv\Scripts\python scripts\audit_final_study_readiness.py
```

## Claim Boundary

Do not cite the packet as calibration evidence. It documents evidence gaps and
review priorities. Final-study claims remain blocked until weak values are
source-strengthened or explicitly accepted in `data/parameters/parameter_acceptance.csv`
within a conservative, not-operational claim boundary.
