# Experiment Strategy Readiness Packet

Experiment strategy-readiness packet only; not experiment acceptance, not calibrated real-world validation, not operational routing evidence, and not publication-readiness approval. This packet cannot close data/manifests/experiment_acceptance.json.

## Verdict

- Publication ready: `false`
- Can mark complete: `false`
- Review rows: 9
- Blocking requests: 4
- Human-review requests: 5
- Status counts: `{'blocked_graph_scale_dependency': 1, 'blocked_input_evidence_dependency': 1, 'blocked_missing_experiment_acceptance_record': 1, 'blocked_scaffold_or_not_calibrated_experiment_scope': 1, 'needs_human_review_common_random_numbers': 1, 'needs_human_review_experiment_checksums': 1, 'needs_human_review_experiment_row_counts': 2, 'needs_human_review_scenario_policy_seed_design': 1}`

## Readiness Rows

| Category | Status | Rows | Required Action |
| --- | --- | --- | --- |
| manifest_scope | blocked_scaffold_or_not_calibrated_experiment_scope | 1890 / 1890 | keep experiment claims bounded until formal acceptance chooses final result scope |
| results_row_count | needs_human_review_experiment_row_counts | 1890 / 1890 | confirm row counts are generated from the selected accepted run profile |
| summary_row_count | needs_human_review_experiment_row_counts | 63 / 63 | confirm row counts are generated from the selected accepted run profile |
| scenario_policy_seed_design | needs_human_review_scenario_policy_seed_design | 1890 / 1890 | review scenario, policy, seed, and exclusion design before acceptance |
| graph_scope_dependency | blocked_graph_scale_dependency | 118 / 4608 | close graph-scale acceptance or regenerate outputs on the accepted graph method |
| input_evidence_dependency | blocked_input_evidence_dependency | 7 / 5 | close upstream input-evidence gates before accepting full experiment outputs |
| common_random_numbers | needs_human_review_common_random_numbers | 30 / 30 | review seed pairing and scenario runner RNG splitting before paired claims |
| artifact_checksums | needs_human_review_experiment_checksums | 3 / 3 | record checksums or regenerated equivalents in formal experiment acceptance |
| formal_experiment_acceptance_requirement | blocked_missing_experiment_acceptance_record | 0 / 1 | create a formal acceptance record only after reviewer decision |

## Required Reviewer Actions

- Keep full-pilot outputs in scaffold scope until graph-scale, input-evidence, validation, and experiment acceptance records exist.
- Decide whether the current full-profile run is accepted, regenerated on another graph method, or retained only as review evidence.
- Review row counts, checksums, scenario-policy-seed design, and CRN pairing before formal experiment acceptance.
- Do not create formal acceptance artifacts from this readiness packet alone.
