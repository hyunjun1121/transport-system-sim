# Sensitivity Strategy Review Packet

Sensitivity strategy review packet only; not sensitivity acceptance, not calibrated real-world sensitivity evidence, not a Sobol waiver, not operational routing evidence, and not publication-readiness approval. This packet cannot close data/manifests/sensitivity_acceptance.json.

## Verdict

- Publication ready: `false`
- Can mark complete: `false`
- Review rows: 7
- Blocking requests: 2
- Human-review requests: 5
- Status counts: `{'blocked_missing_morris_vs_sobol_decision': 1, 'blocked_reduced_graph_scope_for_sensitivity_claims': 1, 'needs_human_review_morris_artifact_selection': 1, 'needs_human_review_sensitivity_acceptance_record': 1, 'needs_human_review_sensitivity_result_scope': 1, 'needs_human_review_unavailable_morris_indices': 1, 'needs_human_review_zero_mu_star_interpretation': 1}`

## Review Rows

| Category | Status | Affected Rows | Required Action |
| --- | --- | --- | --- |
| structural_readiness | needs_human_review_morris_artifact_selection | 0 | confirm these Morris artifacts correspond to the selected study-closeout sensitivity run |
| missing_or_nonfinite_morris_indices | needs_human_review_unavailable_morris_indices | 4832 | document why the affected Morris indices are unavailable and how those rows are handled in tables and claims |
| zero_mu_star_rows | needs_human_review_zero_mu_star_interpretation | 33619 | interpret zero-effect rows before claiming parameter influence or no-effect findings |
| reduced_graph_scope | blocked_reduced_graph_scope_for_sensitivity_claims | 61824 | close graph-scale decision review or regenerate sensitivity outputs on the reviewer-selected graph method |
| result_scope | needs_human_review_sensitivity_result_scope | 61824 | review result scope wording before manuscript use |
| sobol_decision_requirement | blocked_missing_morris_vs_sobol_decision | 61824 | decide whether Morris screening is sufficient or Sobol analysis is required |
| sensitivity_acceptance_record | needs_human_review_sensitivity_acceptance_record |  | validate the existing sensitivity acceptance record |

## Required Reviewer Actions

- Decide whether current Morris screening is enough for the reviewer-selected claim boundary or whether Sobol analysis must be run.
- Resolve unavailable, missing, or non-finite Morris index handling before using sensitivity rankings in the manuscript.
- Review zero `mu_star` rows as diagnostics, not as calibrated no-effect findings.
- Keep sensitivity outputs in scaffold scope until graph-scale, parameter, and sensitivity decision records exist.
- Do not create formal acceptance artifacts from this review packet alone.
