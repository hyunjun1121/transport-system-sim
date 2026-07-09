# Experiment Strategy Review Packet

Experiment strategy review packet only; not an experiment decision record, not field-fit real-world evidence, not route-command evidence, and not publication gate evidence. This packet cannot close data/manifests/experiment_acceptance.json.

## Verdict

- Publication gate supported: `false`
- Can mark complete: `false`
- Review rows: 9
- Blocking requests: 3
- Human-review requests: 6
- Status counts: `{'blocked_graph_scale_dependency': 1, 'blocked_input_evidence_dependency': 1, 'blocked_scaffold_or_not_calibrated_experiment_scope': 1, 'needs_human_review_common_random_numbers': 1, 'needs_human_review_experiment_acceptance_record': 1, 'needs_human_review_experiment_checksums': 1, 'needs_human_review_experiment_row_counts': 2, 'needs_human_review_scenario_policy_seed_design': 1}`

## Strategy Review Rows

| Category | Status | Rows | Required Action |
| --- | --- | --- | --- |
| manifest_scope | blocked_scaffold_or_not_calibrated_experiment_scope | 12420 / 12420 | keep experiment claims bounded until a formal experiment decision chooses the release-scope result set |
| results_row_count | needs_human_review_experiment_row_counts | 12420 / 12420 | confirm row counts are generated from the selected run profile |
| summary_row_count | needs_human_review_experiment_row_counts | 414 / 414 | confirm row counts are generated from the selected run profile |
| scenario_policy_seed_design | needs_human_review_scenario_policy_seed_design | 12420 / 12420 | review scenario, policy, seed, and exclusion design before an experiment decision |
| graph_scope_dependency | blocked_graph_scale_dependency | 2850 / 197823 | resolve graph-scale decision or regenerate outputs on the selected graph method |
| input_evidence_dependency | blocked_input_evidence_dependency | 16 / 5 | resolve upstream input-evidence gates before promoting full experiment outputs |
| common_random_numbers | needs_human_review_common_random_numbers | 30 / 30 | review seed pairing and scenario runner RNG splitting before paired claims |
| artifact_checksums | needs_human_review_experiment_checksums | 3 / 3 | record checksums or regenerated equivalents in the formal experiment decision record |
| formal_experiment_acceptance_requirement | needs_human_review_experiment_acceptance_record | 1 / 1 | review the existing experiment decision record |

## Required Reviewer Actions

- Keep full-pilot outputs in scaffold scope until graph-scale, input-evidence, benchmark, and experiment decision records exist.
- Decide whether the current full-profile run is promoted, regenerated on another graph method, or retained only as review evidence.
- Review row counts, checksums, scenario-policy-seed design, and CRN pairing before a formal experiment decision record.
- Do not create formal decision artifacts from this strategy review packet alone.
