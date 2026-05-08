# Reproducibility Decision Packet

Reproducibility decision packet only; not reproducibility acceptance, not clean-environment certification, not artifact-regeneration acceptance, not final-study approval, and not operational routing evidence. It cannot create or replace data/manifests/reproducibility_acceptance.json.

## Verdict

- Publication ready: `false`
- Can mark complete: `false`
- Decision rows: 7
- Blocking decisions: 4
- Human-review decisions: 3
- Status counts: `{'blocked_artifact_regeneration_not_tested': 1, 'blocked_bounded_or_stale_clean_checkout_evidence': 1, 'blocked_missing_reproducibility_acceptance_record': 1, 'blocked_scaffold_reproducibility_manifest_scope': 1, 'needs_human_review_command_ladder_scope': 1, 'needs_human_review_committed_package_state': 1, 'needs_human_review_runtime_import_boundary': 1}`

## Decision Rows

| Decision | Status | Evidence | Required Action |
| --- | --- | --- | --- |
| reproducibility_manifest_scope_decision | blocked_scaffold_reproducibility_manifest_scope | scope=scaffold-only real-world pilot package; review_scope=scaffold-only real-world pilot package; review_status_counts={'blocked_dirty_worktree': 1, 'blocked_full_clean_checkout_not_run': 1, 'blocked_no_reproducibility_acceptance_record': 1, 'blocked_scaffold_only_manifest_scope': 1, 'blocked_untracked_reproducibility_artifacts': 1, 'ready_for_review_bounded_clean_checkout_smoke': 1, 'ready_for_review_command_ladder_present': 1, 'ready_for_review_no_cloned_repo_runtime_imports': 1} | Review the manifest scope, command ladder, and regenerated artifact list before formal reproducibility acceptance. |
| validation_command_ladder_decision | needs_human_review_command_ladder_scope | command_count=46; validation_command_count=72; clean_checkout_smoke_command_count=9 | Compare manifest command counts with the planned validation ladder and decide whether additional clean-checkout commands are required. |
| clean_checkout_evidence_scope_decision | blocked_bounded_or_stale_clean_checkout_evidence | clean_checkout_test_performed=true; clean_checkout_smoke_passed=true; matches_review_head=false; source_commit_relation=ancestor_of_review_head; source_commit_lag_count=18; full_clean_environment_tested=false; dependency_install_tested=false; source_commit=2be0bbe0fbca879d345f0a5a16f5d3741c21950b | Decide whether to rerun clean-checkout smoke at the current commit and whether a full dependency reinstall is required. |
| worktree_package_state_decision | needs_human_review_committed_package_state | git_status_line_count=77; git_modified_or_staged_count=71; git_untracked_count=6 | Confirm the final package is committed, clean, and contains or explicitly excludes all required generated artifacts. |
| runtime_import_boundary_decision | needs_human_review_runtime_import_boundary | no_runtime_cloned_repo_imports=true; runtime_cloned_repo_import_hits=[] | Review cloned_repo import scan results and preserve cloned_repo as reference-only context. |
| artifact_regeneration_decision | blocked_artifact_regeneration_not_tested | clean_checkout_artifact_regeneration_tested=false; clean_checkout_dependency_install_tested=false; worktree_smoke_passed=true; worktree_smoke_command_count=26 | Run or review artifact-regeneration commands before formal reproducibility acceptance. |
| formal_reproducibility_acceptance_boundary | blocked_missing_reproducibility_acceptance_record | reproducibility_acceptance_present=false | Record formal reproducibility acceptance only after placeholders are absent and the reviewer accepts the reproduction scope. |

## Boundary

- This packet does not approve reproducibility or final-study completion.
- It does not replace clean-checkout, full clean-environment, artifact-regeneration, or formal acceptance review.
- Keep `data/manifests/reproducibility_acceptance.json` absent until a reviewer accepts the reproduction scope.
