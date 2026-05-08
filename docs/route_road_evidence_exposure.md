# Canonical Route Road-Evidence Exposure

> Current project status (2026-05-08): `final_study_ready=false`. Ready gates are `3/15` (`real_input_smoke`, `structured_disruptions`, `policy_alternatives`), blocked gates are `12/15`, and formal acceptance is `0/12` ready. This document is current-state or review support only; it does not create formal approval, calibrated real-world results, or operational routing guidance.


## Scope

`data/validation/canonical_route_road_evidence_exposure.csv` links current
road-evidence gaps to the canonical route candidates used in graph-scale
review. It is a prioritization worksheet for road-input review.

It is not accepted road calibration, benchmark validation, graph-scale
acceptance, or operational routing evidence.

## Generated Artifacts

| Artifact | Role | Current Scope |
| --- | --- | --- |
| `data/validation/canonical_route_road_evidence_exposure.csv` | Route-level exposure worksheet | review support only |
| `data/validation/canonical_route_road_evidence_exposure_summary.md` | Human-readable snapshot summary | review support only |
| `data/validation/canonical_route_road_evidence_exposure_manifest.json` | Counts, inputs, outputs, and claim boundary | review support only |
| `scripts/write_route_road_evidence_exposure.py` | Regenerates the worksheet, summary, and manifest | deterministic scaffold command |
| `src/realworld/route_road_evidence_exposure.py` | Library implementation | project-owned code |

## Current Snapshot

The current worksheet has 76 rows across 18 route candidates. It covers both
the current reduced corridor and the multi-corridor candidate graph-scale
tables. Every exposure row remains weak for final-study claims because current
road speed, capacity, disruption, and connector evidence is still review-stage.

## Interpretation

Use this worksheet to identify which weak road classes dominate the canonical
`A -> D`, `A -> S`, and `R -> D` route candidates by distance or time. It
complements the road-class review packet by making the route-level consequence
of weak evidence visible.

Final road-input claims still require reviewed road-class evidence, accepted
override application when needed, validation-package acceptance, and
graph-scale acceptance.

## Regeneration

```powershell
.\.venv\Scripts\python scripts\write_route_road_evidence_exposure.py
.\.venv\Scripts\python tests\test_realworld_route_road_evidence_exposure.py
```

Do not use this artifact to create `data/manifests/validation_acceptance.json`
or `data/manifests/graph_scale_acceptance.json` by itself.
