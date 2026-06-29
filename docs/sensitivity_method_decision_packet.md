# Sensitivity Method Decision Packet

Sensitivity method-decision packet only; not sensitivity acceptance, not a Sobol waiver, not calibrated real-world sensitivity evidence, and not operational routing evidence. It cannot create data/manifests/sensitivity_acceptance.json.

## Verdict

- Publication ready: `false`
- Can mark complete: `false`
- Sobol decision recorded: `false`
- Sobol waiver created: `false`
- Decision rows: 7
- Blocking decisions: 2
- Human-review decisions: 5
- Status counts: `{'blocked_missing_morris_vs_sobol_decision': 1, 'blocked_reduced_graph_scope_dependency': 1, 'needs_human_review_defer_or_continue': 1, 'needs_human_review_existing_sensitivity_acceptance': 1, 'needs_human_review_index_handling_policy': 1, 'needs_human_review_morris_screening_scope': 1, 'needs_human_review_result_scope': 1}`

## Decision Rows

| Decision | Status | Candidate | Required Action |
| --- | --- | --- | --- |
| retain_morris_screening_option | needs_human_review_morris_screening_scope | Treat current Morris output as screening evidence inside a reviewed scaffold or final-study claim boundary | Decide whether Morris screening is sufficient for the intended claim boundary after graph, parameter, and index-handling review. |
| run_sobol_extension_option | blocked_missing_morris_vs_sobol_decision | Run Sobol first-order and total-order analysis before final sensitivity acceptance | Choose whether Sobol is required, then define compute budget, sample design, output metrics, and interpretation rules if it is run. |
| defer_sensitivity_acceptance_option | needs_human_review_defer_or_continue | Keep sensitivity acceptance blocked until upstream evidence and method scope are reviewed | Confirm whether to defer final sensitivity claims or collect additional Morris/Sobol evidence. |
| index_handling_policy | needs_human_review_index_handling_policy | Document treatment of unavailable indices and zero-effect rows before ranking parameters | Decide whether unavailable p80/p95 rows are excluded, retained as unavailable diagnostics, or regenerated before manuscript use. |
| graph_scope_dependency | blocked_reduced_graph_scope_dependency | Use sensitivity outputs only on the accepted graph-scale method | Close graph-scale acceptance or regenerate sensitivity outputs on the accepted graph method before final sensitivity claims. |
| result_scope_boundary | needs_human_review_result_scope | Keep Morris output scoped as scaffold evidence unless accepted on final input and graph evidence | Keep manuscript/report claims bounded until the formal sensitivity record accepts scope and interpretation. |
| formal_sensitivity_acceptance_boundary | needs_human_review_existing_sensitivity_acceptance | Record the reviewed Morris/Sobol, graph-scope, parameter-range, and index-handling decision only in the formal acceptance path | Create or validate sensitivity_acceptance.json only after source-backed human review; do not copy this packet into the formal path. |

## Boundary

- This packet is a reviewer worksheet, not an acceptance record.
- It does not run Sobol, waive Sobol, accept Morris, or prove parameter dominance.
- Keep final-study claims blocked until `data/manifests/sensitivity_acceptance.json` is reviewed.
