# Reproducibility Smoke Run

`data/validation/reproducibility_smoke_manifest.json` records a bounded
current-worktree smoke run. It is not a clean-checkout reproduction and
does not close `data/manifests/reproducibility_acceptance.json`.

## Summary

- Result scope: `current_worktree_smoke_not_clean_checkout`
- Smoke passed: `true`
- Commands passed: 28 / 28
- Clean checkout tested: `false`
- Can mark complete: `false`

## Command Results

| Command | Status | Return Code |
| --- | --- | --- |
| py_compile_acceptance_reproducibility | passed | 0 |
| test_acceptance_records | passed | 0 |
| test_acceptance_orchestration | passed | 0 |
| test_acceptance_templates | passed | 0 |
| test_acceptance_blocker_queue | passed | 0 |
| test_acceptance_task_assignments | passed | 0 |
| test_agent_review_path_audit | passed | 0 |
| test_formal_acceptance_guard | passed | 0 |
| test_formal_evidence_path_audit | passed | 0 |
| test_formal_acceptance_package | passed | 0 |
| test_formal_acceptance_evidence_matrix | passed | 0 |
| test_formal_acceptance_pre_review | passed | 0 |
| test_goal_completion_audit | passed | 0 |
| test_clean_checkout_smoke | passed | 0 |
| test_final_study_readiness | passed | 0 |
| test_plan_audit | passed | 0 |
| test_publication_readiness | passed | 0 |
| test_reproducibility_review_packet | passed | 0 |
| test_reproducibility_decision_packet | passed | 0 |
| test_final_audit_decision_packet | passed | 0 |
| formal_acceptance_package_audit | passed | 0 |
| formal_evidence_path_audit | passed | 0 |
| agent_review_path_audit | passed | 0 |
| final_study_readiness_audit | passed | 0 |
| acceptance_audit | passed | 0 |
| plan_artifact_audit | passed | 0 |
| runtime_cloned_repo_import_boundary | passed | 0 |
| git_diff_check | passed | 0 |

## Claim Boundary

This is a bounded current-worktree smoke run. It is not a fresh-clone or clean-checkout reproduction, does not create data/manifests/reproducibility_acceptance.json, and does not support calibrated real-world or operational routing claims.

## Required Actions

- run clean-checkout reproduction from a fresh clone or exported package
- preserve command logs for the full validation ladder and artifact regeneration
- review the scaffold-only reproducibility manifest scope
- resolve dirty or untracked worktree state before claiming package reproducibility
- create data/manifests/reproducibility_acceptance.json only after human review accepts the clean-checkout package
