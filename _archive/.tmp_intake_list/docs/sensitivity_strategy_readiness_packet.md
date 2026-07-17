# Sensitivity Strategy Readiness Packet

Sensitivity strategy-readiness packet only; not sensitivity acceptance, not calibrated real-world sensitivity evidence, not a Sobol waiver, not operational routing evidence, and not publication-readiness approval. This packet cannot close data/manifests/sensitivity_acceptance.json.

## Verdict

- Publication ready: `false`
- Can mark complete: `false`
- Review rows: 7
- Blocking requests: 4
- Human-review requests: 3
- Status counts: `{'blocked_missing_morris_vs_sobol_decision': 1, 'blocked_missing_sensitivity_acceptance_record': 1, 'blocked_reduced_graph_scope_for_sensitivity_claims': 1, 'blocked_scaffold_or_not_calibrated_result_scope': 1, 'needs_human_review_morris_artifact_selection': 1, 'needs_human_review_unavailable_morris_indices': 1, 'needs_human_review_zero_mu_star_interpretation': 1}`

## Readiness Rows

| Category | Status | Affected Rows | Required Action |
| --- | --- | --- | --- |
| structural_readiness | needs_human_review_morris_artifact_selection | 0 | confirm these Morris artifacts correspond to the selected final-study sensitivity run |
| missing_or_nonfinite_morris_indices | needs_human_review_unavailable_morris_indices | 168 | document why the affected Morris indices are unavailable and how those rows are handled in tables and claims |
| zero_mu_star_rows | needs_human_review_zero_mu_star_interpretation | 4272 | interpret zero-effect rows before claiming parameter influence or no-effect findings |
| reduced_graph_scope | blocked_reduced_graph_scope_for_sensitivity_claims | 7056 | close graph-scale acceptance or regenerate sensitivity outputs on the accepted graph method |
| result_scope | blocked_scaffold_or_not_calibrated_result_scope | 7056 | keep final claims bounded until sensitivity results are accepted on final evidence scope |
| sobol_decision_requirement | blocked_missing_morris_vs_sobol_decision | 7056 | decide whether Morris screening is sufficient or Sobol analysis is required |
| sensitivity_acceptance_record | blocked_missing_sensitivity_acceptance_record |  | record method, graph scope, parameter-range, SALib-output, index-handling, and Sobol decisions only after review |

## Required Reviewer Actions

- Decide whether current Morris screening is enough for the accepted claim boundary or whether Sobol analysis must be run.
- Resolve unavailable, missing, or non-finite Morris index handling before using sensitivity rankings in the manuscript.
- Review zero `mu_star` rows as diagnostics, not as calibrated no-effect findings.
- Keep sensitivity outputs in scaffold scope until graph-scale, parameter, and sensitivity acceptance records exist.
- Do not create formal acceptance artifacts from this readiness packet alone.
