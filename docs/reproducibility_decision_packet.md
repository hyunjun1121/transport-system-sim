# Reproducibility Decision Packet

Reproducibility decision packet only; not reproducibility acceptance, not clean-environment certification, not artifact-regeneration acceptance, not final-study approval, and not operational routing evidence. It cannot create or replace data/manifests/reproducibility_acceptance.json.

## Verdict

- Publication ready: `false`
- Can mark complete: `false`
- Decision rows: 7
- Blocking decisions: 0
- Human-review decisions: 7
- Status counts: `{'needs_human_review_artifact_regeneration': 1, 'needs_human_review_clean_checkout_evidence_scope': 1, 'needs_human_review_command_ladder_scope': 1, 'needs_human_review_committed_package_state': 1, 'needs_human_review_formal_reproducibility_acceptance': 1, 'needs_human_review_reproducibility_manifest_scope': 1, 'needs_human_review_runtime_import_boundary': 1}`

## Decision Rows

| Decision | Status | Evidence | Required Action |
| --- | --- | --- | --- |
| reproducibility_manifest_scope_decision | needs_human_review_reproducibility_manifest_scope | scope=Reviewer-accepted real-world pilot reproduction package within formal-acceptance claim boundary; review_scope=Reviewer-accepted real-world pilot reproduction package within formal-acceptance claim boundary; review_status_counts={'blocked_dirty_worktree': 1, 'blocked_full_clean_checkout_not_run': 1, 'blocked_untracked_reproducibility_artifacts': 1, 'ready_for_review_command_ladder_present': 1, 'ready_for_review_full_clean_checkout_smoke': 1, 'ready_for_review_no_cloned_repo_runtime_imports': 1, 'ready_for_review_non_scaffold_manifest_scope': 1, 'review_required_existing_acceptance_record_is_separate': 1} | Review the manifest scope, command ladder, and regenerated artifact list before formal reproducibility acceptance. |
| command_ladder_scope_decision | needs_human_review_command_ladder_scope | command_count=46; validation_command_count=72; clean_checkout_smoke_command_count=9 | Compare manifest command counts with the planned command ladder and decide whether additional clean-checkout commands are required. |
| clean_checkout_evidence_scope_decision | needs_human_review_clean_checkout_evidence_scope | clean_checkout_test_performed=true; clean_checkout_smoke_passed=true; matches_review_head=false; source_commit_relation=ancestor_of_review_head; source_commit_lag_count=22; freshness_reference=last_clean_checkout_smoke_source_commit; full_clean_environment_tested=true; dependency_install_tested=true; source_commit=55327c4bbbd64c907ff8bbfce08ca882a71437f4 | Decide whether the clean-checkout smoke commit relation is review-bounded and whether a full dependency reinstall is required. |
| worktree_package_state_decision | needs_human_review_committed_package_state | git_status_line_count=234; git_modified_or_staged_count=225; git_untracked_count=9 | Confirm the release-scope package is committed, clean, and contains or explicitly excludes all required generated artifacts. |
| runtime_import_boundary_decision | needs_human_review_runtime_import_boundary | no_runtime_cloned_repo_imports=true; runtime_cloned_repo_import_hits=[] | Review cloned_repo import scan results and preserve cloned_repo as reference-only context. |
| artifact_regeneration_decision | needs_human_review_artifact_regeneration | clean_checkout_artifact_regeneration_tested=true; clean_checkout_dependency_install_tested=true; worktree_smoke_passed=true; worktree_smoke_command_count=9 | Run or review artifact-regeneration commands before formal reproducibility acceptance. |
| formal_reproducibility_acceptance_boundary | needs_human_review_formal_reproducibility_acceptance | reproducibility_acceptance_present=true | Record formal reproducibility acceptance only after placeholders are absent and the reviewer records the reproduction scope. |

## Boundary

- This packet does not approve reproducibility or study-closeout completion.
- It does not replace clean-checkout, full clean-environment, artifact-regeneration, or formal acceptance review.
- Keep `data/manifests/reproducibility_acceptance.json` absent until a reviewer records the reproduction scope.
