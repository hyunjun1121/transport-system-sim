# Full Graph Runtime Readiness Packet

Full-graph runtime-readiness packet only; not full-graph experiment output, not graph-scale acceptance, not calibrated validation, and not operational routing evidence. This packet cannot close data/manifests/graph_scale_acceptance.json.

## Verdict

- Publication ready: `false`
- Can mark complete: `false`
- Review rows: 4
- Blocking requests: 2
- Human-review requests: 2
- Status counts: `{'blocked_missing_downstream_full_graph_regeneration_decision': 1, 'blocked_missing_full_graph_full_profile_outputs': 1, 'needs_human_review_full_graph_runtime_scope_decision': 1, 'needs_human_review_full_graph_smoke_scope': 1}`

## Readiness Rows

| Item | Status | Evidence | Required Action |
| --- | --- | --- | --- |
| full_graph_smoke_execution | needs_human_review_full_graph_smoke_scope | data/validation/full_graph_smoke_manifest.json | review the two-row smoke as feasibility evidence only |
| full_graph_full_profile_outputs | blocked_missing_full_graph_full_profile_outputs | results/realworld_pilot/pilot_full_graph_manifest.json | generate full-graph outputs or formally bound final claims away from full-graph execution |
| full_graph_runtime_scope_decision | needs_human_review_full_graph_runtime_scope_decision | data/validation/full_graph_smoke_manifest.json | decide whether the measured smoke supports excluding full-graph full-profile execution or whether full outputs must be generated |
| full_graph_downstream_regeneration | blocked_missing_downstream_full_graph_regeneration_decision | results/realworld_pilot/pilot_full_graph_manifest.json | record downstream regeneration requirements after graph-scale method selection |

## Required Reviewer Actions

- Do not treat smoke runtime as full-profile full-graph evidence.
- Select full graph, reduced corridor, multi-corridor candidate, or an explicitly bounded scope only in the formal graph-scale acceptance record.
- Re-run affected downstream outputs after the accepted graph method is selected.
