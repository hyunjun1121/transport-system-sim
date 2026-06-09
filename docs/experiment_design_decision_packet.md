# Experiment Design Decision Packet

Experiment design-decision packet only; not experiment acceptance, not calibrated real-world results, not graph-scale acceptance, and not operational routing evidence. It cannot create data/manifests/experiment_acceptance.json.

## Verdict

- Publication ready: `false`
- Can mark complete: `false`
- Selected run profile recorded: `false`
- Scenario-policy-seed decision recorded: `false`
- Decision rows: 8
- Blocking decisions: 4
- Human-review decisions: 4
- Status counts: `{'blocked_graph_scale_dependency': 1, 'blocked_input_evidence_dependency': 1, 'blocked_missing_experiment_acceptance_record': 1, 'blocked_scaffold_or_not_calibrated_experiment_scope': 1, 'needs_human_review_current_full_profile_scope': 1, 'needs_human_review_multi_corridor_profile_scope': 1, 'needs_human_review_regenerate_or_retain_outputs': 1, 'needs_human_review_scenario_policy_seed_design': 1}`

## Decision Rows

| Decision | Status | Candidate | Required Action |
| --- | --- | --- | --- |
| sample_staged_full_profile_context | needs_human_review_current_full_profile_scope | Use sample and staged outputs as implementation checks, and treat the current full_pilot profile as the candidate full scenario-policy-seed run only after review | Decide whether the current full_pilot run profile is retained, regenerated, or kept as scaffold-only evidence. |
| multi_corridor_profile_option | needs_human_review_multi_corridor_profile_scope | Use the multi-corridor full-profile candidate only if graph-scale review selects that method | Choose whether the single-corridor full output, multi-corridor full candidate, or a regenerated output should support the experiment package. |
| scenario_policy_seed_design | needs_human_review_scenario_policy_seed_design | Use the current 7-policy, 9-scenario, 30-seed common-random-number full design as the candidate reviewed design | Review policy exclusions, scenario scope, seed count, CRN pairing, and row-count multiplication before experiment-gate review. |
| graph_scope_dependency | blocked_graph_scale_dependency | Use experiment outputs only on the graph-scale method chosen by formal graph-scale review | Provide graph-scale review record or regenerate outputs on the selected graph method before experiment-output review. |
| input_evidence_dependency | blocked_input_evidence_dependency | Use current experiment outputs only after upstream input, road override, parameter, validation, and provenance gates close | Close upstream evidence gates or document why current outputs remain scaffold-only. |
| result_scope_boundary | blocked_scaffold_or_not_calibrated_experiment_scope | Keep current full-pilot outputs scoped as scaffold or decision-support evidence until formal acceptance revises the claim boundary | Keep manuscript/report claims bounded until experiment acceptance records the reviewed result scope. |
| regenerate_or_retain_outputs | needs_human_review_regenerate_or_retain_outputs | Decide whether to retain current outputs, regenerate after graph/input review, or keep them only as review evidence | Record whether reviewed outputs should use the current full_pilot run, a multi-corridor/full-graph rerun, or a later regenerated package. |
| formal_experiment_acceptance_boundary | blocked_missing_experiment_acceptance_record | Record the selected run profile, graph scope, design, CRN, counts, checksums, and claim boundary only in the formal experiment acceptance path | Create or validate experiment_acceptance.json only after source-backed human review; do not copy this packet into the formal path. |

## Boundary

- This packet is a reviewer worksheet, not an acceptance record.
- It does not select a final run profile, accept graph scope, or approve scenario-policy-seed design.
- Keep full-experiment claims blocked until `data/manifests/experiment_acceptance.json` is reviewed.
