# Reproducibility Decision Packet

Reproducibility decision packet only; not reproducibility acceptance, not clean-environment certification, not artifact-regeneration acceptance, not final-study approval, and not operational routing evidence. It cannot create or replace data/manifests/reproducibility_acceptance.json.

## Verdict

- Publication ready: `false`
- Can mark complete: `false`
- Decision rows: 7
- Blocking decisions: 2
- Human-review decisions: 5
- Status counts: `{'blocked_missing_reproducibility_acceptance_record': 1, 'blocked_scaffold_reproducibility_manifest_scope': 1, 'needs_human_review_artifact_regeneration': 1, 'needs_human_review_clean_checkout_evidence_scope': 1, 'needs_human_review_command_ladder_scope': 1, 'needs_human_review_committed_package_state': 1, 'needs_human_review_runtime_import_boundary': 1}`

## Decision Rows

| Decision | Status | Evidence | Required Action |
| --- | --- | --- | --- |
| reproducibility_manifest_scope_decision | blocked_scaffold_reproducibility_manifest_scope | scope=scaffold-only real-world pilot package; review_scope=scaffold-only real-world pilot package; review_status_counts={'blocked_full_clean_checkout_not_run': 1, 'blocked_no_reproducibility_acceptance_record': 1, 'blocked_scaffold_only_manifest_scope': 1, 'ready_for_review_clean_worktree': 1, 'ready_for_review_command_ladder_present': 1, 'ready_for_review_full_clean_checkout_smoke': 1, 'ready_for_review_no_cloned_repo_runtime_imports': 1, 'ready_for_review_no_untracked_reproducibility_artifacts': 1} | Review the manifest scope, command ladder, and regenerated artifact list before formal reproducibility acceptance. |
| validation_command_ladder_decision | needs_human_review_command_ladder_scope | command_count=46; validation_command_count=72; clean_checkout_smoke_command_count=9 | Compare manifest command counts with the planned validation ladder and decide whether additional clean-checkout commands are required. |
| clean_checkout_evidence_scope_decision | needs_human_review_clean_checkout_evidence_scope | clean_checkout_test_performed=true; clean_checkout_smoke_passed=true; matches_review_head=false; source_commit_relation=ancestor_of_review_head; source_commit_lag_count=6; full_clean_environment_tested=true; dependency_install_tested=true; source_commit=b7eece48de42ea46675bb15cc72e9a767fdb90df | Decide whether the clean-checkout smoke commit relation is acceptable and whether a full dependency reinstall is required. |
| worktree_package_state_decision | needs_human_review_committed_package_state | git_status_line_count=0; git_modified_or_staged_count=0; git_untracked_count=0 | Confirm the final package is committed, clean, and contains or explicitly excludes all required generated artifacts. |
| runtime_import_boundary_decision | needs_human_review_runtime_import_boundary | no_runtime_cloned_repo_imports=true; runtime_cloned_repo_import_hits=[] | Review cloned_repo import scan results and preserve cloned_repo as reference-only context. |
| artifact_regeneration_decision | needs_human_review_artifact_regeneration | clean_checkout_artifact_regeneration_tested=true; clean_checkout_dependency_install_tested=true; worktree_smoke_passed=true; worktree_smoke_command_count=28 | Run or review artifact-regeneration commands before formal reproducibility acceptance. |
| formal_reproducibility_acceptance_boundary | blocked_missing_reproducibility_acceptance_record | reproducibility_acceptance_present=false | Record formal reproducibility acceptance only after placeholders are absent and the reviewer accepts the reproduction scope. |

## Boundary

- This packet does not approve reproducibility or final-study completion.
- It does not replace clean-checkout, full clean-environment, artifact-regeneration, or formal acceptance review.
- Keep `data/manifests/reproducibility_acceptance.json` absent until a reviewer accepts the reproduction scope.
