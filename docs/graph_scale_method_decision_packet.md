# Graph-Scale Method Decision Packet

Graph-scale method-decision packet only; not graph-scale acceptance, not calibrated real-world validation, not traffic model validation, and not operational routing evidence. It cannot create data/manifests/graph_scale_acceptance.json.

## Verdict

- Publication ready: `false`
- Can mark complete: `false`
- Selected graph method recorded: `false`
- Downstream regeneration decision recorded: `false`
- Decision rows: 7
- Blocking decisions: 4
- Human-review decisions: 3
- Status counts: `{'blocked_incomplete_multi_corridor_run_profile': 1, 'blocked_missing_downstream_regeneration_decision': 1, 'blocked_missing_full_graph_full_profile_outputs': 1, 'blocked_missing_graph_scale_acceptance_record': 1, 'needs_human_review_graph_sensitive_result_deltas': 1, 'needs_human_review_multi_corridor_result_delta_policy': 1, 'needs_human_review_reduced_corridor_warning_policy': 1}`

## Decision Rows

| Decision | Status | Candidate | Required Action |
| --- | --- | --- | --- |
| current_reduced_corridor_method_option | needs_human_review_reduced_corridor_warning_policy | Accept the current 118-node reduced corridor only if omitted alternate paths are immaterial under a documented corridor-selection rule | Decide whether the six alternate-route warning rows are acceptable or require a broader graph method. |
| multi_corridor_candidate_method_option | blocked_incomplete_multi_corridor_run_profile | Use the 164-node multi-corridor graph only after deciding whether the separated candidate output is sufficient or a full-profile run is required | Use the existing full-profile candidate, regenerate the accepted output package on this graph, or exclude this option. |
| multi_corridor_full_candidate_method_option | needs_human_review_multi_corridor_result_delta_policy | Replace the current reduced corridor with the full-profile multi-corridor candidate if result deltas are reviewed and downstream artifacts are regenerated as needed | Review candidate_worsens and nonfinite result differences before selecting the multi-corridor full-profile method. |
| full_bus_practical_graph_method_option | blocked_missing_full_graph_full_profile_outputs | Use the full 4,608-node bus-practical graph only if full scenario-policy-seed outputs are generated or formally excluded from scope | Generate full-graph outputs or record in the formal graph-scale acceptance why full-graph execution is outside scope. |
| graph_sensitive_result_interpretation | needs_human_review_graph_sensitive_result_deltas | Interpret policy outcomes only after selecting a graph method and reviewing current-vs-candidate result differences | Decide whether changed outcomes reflect a better graph abstraction or a scenario-method interaction that requires additional runs. |
| downstream_regeneration_scope | blocked_missing_downstream_regeneration_decision | Regenerate or explicitly retain sensitivity, figures, tables, experiment summaries, and manuscript interpretation after the accepted graph method is selected | Record which downstream artifacts will be regenerated, retained as review evidence, or excluded from final claims. |
| formal_graph_scale_acceptance_boundary | blocked_missing_graph_scale_acceptance_record | Record the selected graph-scale method, source graph counts, analysis graph counts, evidence paths, and claim boundary only in the formal acceptance path | Create or validate graph_scale_acceptance.json only after source-backed human review; do not copy this packet into the formal path. |

## Boundary

- This packet is a reviewer worksheet, not an acceptance record.
- It does not select a graph method, approve full-graph exclusion, or accept downstream regeneration scope.
- Keep graph-scale claims blocked until `data/manifests/graph_scale_acceptance.json` is reviewed.
