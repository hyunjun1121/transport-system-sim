# Graph-Scale Strategy Readiness Packet

Graph-scale strategy-readiness packet only; not graph-scale acceptance, not calibrated real-world validation, not traffic model validation, not operational routing evidence, and not publication-readiness approval. This packet cannot close data/manifests/graph_scale_acceptance.json.

## Verdict

- Publication ready: `false`
- Can mark complete: `false`
- Review rows: 5
- Blocking requests: 2
- Human-review requests: 3
- Status counts: `{'blocked_missing_full_graph_experiment_outputs': 1, 'blocked_missing_graph_scale_acceptance_record': 1, 'needs_human_review_multi_corridor_result_deltas': 1, 'needs_human_review_multi_corridor_sample_scope': 1, 'needs_human_review_reduced_corridor_alternate_route_warnings': 1}`

## Full-Graph Runtime Readiness

- Manifest present: `true`
- Blocking requests: 2
- Human-review requests: 2
- Can mark complete: `false`

## Readiness Rows

| Option | Status | Evidence | Required Action |
| --- | --- | --- | --- |
| current_reduced_corridor | needs_human_review_reduced_corridor_alternate_route_warnings | baseline route parity passes; alternate-route diagnostic has warning rows; full pilot scaffold outputs exist | review whether omitted alternate paths are acceptable or require multi-corridor/full-graph execution |
| multi_corridor_candidate | needs_human_review_multi_corridor_sample_scope | top-3 route candidates are preserved; small separated candidate experiment output exists | treat the separated candidate as route-preservation/smoke evidence and review the full-profile candidate before method selection |
| multi_corridor_full_candidate | needs_human_review_multi_corridor_result_deltas | top-3 route candidates are preserved; full scenario-policy-seed candidate output exists on the multi-corridor graph | review candidate_worsens and nonfinite result differences before accepting this graph method |
| full_bus_practical_graph | blocked_missing_full_graph_experiment_outputs | full graph smoke manifest reports 2 rows on 4608 nodes / 9148 edges; full scenario-policy-seed outputs have not been generated on the full graph | generate full-graph outputs or explicitly bound final claims away from full-graph execution |
| graph_scale_acceptance_record | blocked_missing_graph_scale_acceptance_record | data/manifests/graph_scale_acceptance.json | record the selected graph-scale method only after source-vs-analysis graph review |

## Required Reviewer Actions

- Choose the accepted graph-scale method only after reviewing route preservation, result deltas, runtime scope, and downstream regeneration impact.
- Keep reduced-corridor and multi-corridor outputs in scaffold scope until the selected method is formally accepted.
- Do not treat this packet as graph-scale acceptance or calibrated network validation.
