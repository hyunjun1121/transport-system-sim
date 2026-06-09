# Reproducibility Smoke Run

`data/validation/reproducibility_smoke_manifest.json` records a bounded
current-worktree smoke run. It is not a clean-checkout reproduction and
does not close `data/manifests/reproducibility_acceptance.json`.

## Summary

- Result scope: `current_worktree_smoke_not_clean_checkout`
- Smoke passed: `true`
- Commands passed: 9 / 9
- Clean checkout tested: `false`
- Can mark complete: `false`

## Command Results

| Command | Status | Return Code |
| --- | --- | --- |
| py_compile_clean_checkout_evidence | passed | 0 |
| test_clean_checkout_smoke | passed | 0 |
| test_reproducibility_review_packet | passed | 0 |
| test_final_study_readiness | passed | 0 |
| test_publication_readiness | passed | 0 |
| formal_acceptance_package_audit | passed | 0 |
| final_study_readiness_audit | passed | 0 |
| runtime_cloned_repo_import_boundary | passed | 0 |
| git_diff_check | passed | 0 |

## Claim Boundary

This is a bounded current-worktree smoke run. It is not a fresh-clone or clean-checkout reproduction, does not create data/manifests/reproducibility_acceptance.json, and does not support calibrated real-world or operational routing claims.

## Required Actions

- run clean-checkout reproduction from a fresh clone or exported package
- preserve command logs for the full command ladder and artifact regeneration
- review the scaffold-only reproducibility manifest scope
- resolve dirty or untracked worktree state before claiming package reproducibility
- create data/manifests/reproducibility_acceptance.json only after human review records the clean-checkout package decision
