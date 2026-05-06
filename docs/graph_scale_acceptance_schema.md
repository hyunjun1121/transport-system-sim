# Graph-Scale Acceptance Schema

> Current project status (2026-05-06): `final_study_ready=false`. Ready gates are `3/15` (`real_input_smoke`, `structured_disruptions`, `policy_alternatives`), blocked gates are `12/15`, and formal acceptance is `0/12` ready. This document is current-state or review support only; it does not create formal approval, calibrated real-world results, or operational routing guidance.


Final-study claims require an explicit graph-scale decision before a reduced
analysis graph, full cached graph, or multi-corridor ensemble can be treated as
accepted study input. The current repository intentionally does not commit this
record, so `scripts/audit_final_study_readiness.py` remains blocked.

Expected path:

```text
data/manifests/graph_scale_acceptance.json
```

## Required Fields

| Field | Meaning |
| --- | --- |
| `region_id` | Pilot region identifier matching the accepted region spec. |
| `accepted` | JSON boolean. Must be `true` for final-study readiness. |
| `accepted_by` | Reviewer or team that accepted the graph-scale decision. |
| `accepted_date` | Review date. |
| `graph_scale_decision` | One of `corridor_abstraction`, `full_graph_runtime`, or `multi_corridor_ensemble`. |
| `source_graph_nodes` / `source_graph_edges` | Positive counts for the cached source graph after road-mode filtering. |
| `analysis_graph_nodes` / `analysis_graph_edges` | Positive counts for the actual graph used in experiments. |
| `corridor_reduction_accepted` | JSON boolean. Must be `true` when using `corridor_abstraction`. |
| `alternate_corridor_sensitivity_reviewed` | JSON boolean. Must be `true` when using `corridor_abstraction`. |
| `claim_boundary` | Must state that outputs are not operational routing guidance. |
| `evidence_paths` | Non-empty list of manifests, method notes, or validation artifacts. |

## Example

```json
{
  "region_id": "songpa_public_demo",
  "accepted": true,
  "accepted_by": "reviewer-name-or-team",
  "accepted_date": "2026-05-04",
  "graph_scale_decision": "corridor_abstraction",
  "source_graph_nodes": 4608,
  "source_graph_edges": 9148,
  "analysis_graph_nodes": 118,
  "analysis_graph_edges": 174,
  "corridor_reduction_accepted": true,
  "alternate_corridor_sensitivity_reviewed": true,
  "claim_boundary": "Accepted for quasi-real decision-support study; not operational routing.",
  "evidence_paths": [
    "docs/analysis_corridor_method_note.md",
    "results/realworld_pilot/pilot_full_manifest.json"
  ]
}
```

## Validation

```powershell
.\.venv\Scripts\python tests\test_realworld_graph_scale_acceptance.py
.\.venv\Scripts\python scripts\audit_final_study_readiness.py
```

The final readiness audit should remain blocked until this file exists and the
other final-study evidence gates are also closed.
