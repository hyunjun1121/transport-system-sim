# Clean-Checkout Reproducibility Smoke

`data/validation/clean_checkout_reproducibility_smoke_manifest.json`
records a bounded clean source-checkout smoke run. It is not formal
reproducibility acceptance and does not close
`data/manifests/reproducibility_acceptance.json`.

## Summary

- Result scope: `clean_checkout_source_tree_smoke_not_formal_acceptance`
- Smoke passed: `true`
- Commands passed: 9 / 9
- Clean checkout tested: `true`
- Full clean environment tested: `true`
- Artifact regeneration tested: `true`
- Artifact regeneration scope: `bounded_review_and_audit_artifact_regeneration_not_full_reproduction`
- Source commit: `55327c4bbbd64c907ff8bbfce08ca882a71437f4`
- Environment scope: `clean_source_checkout_fresh_venv_with_dependency_install`
- Can mark complete: `false`

## Outer Steps

| Step | Status | Return Code |
| --- | --- | --- |
| git_clone_source_tree | passed | 0 |
| git_checkout_source_commit | passed | 0 |
| create_clean_checkout_venv | passed | 0 |
| upgrade_clean_checkout_pip | passed | 0 |
| install_clean_checkout_requirements | passed | 0 |
| run_reproducibility_smoke_in_clean_checkout | passed | 0 |
| regenerate_reproducibility_review_packet | passed | 0 |
| regenerate_reproducibility_decision_packet | passed | 0 |
| regenerate_final_audit_decision_packet | passed | 0 |
| regenerate_acceptance_audit | passed | 0 |

## Inner Smoke

- Inner scope: `current_worktree_smoke_not_clean_checkout`
- Failed commands: ``

## Claim Boundary

This is bounded clean source-checkout smoke evidence. It tests the committed source tree in a fresh clone with a fresh virtual environment and dependency installation, but it does not execute the full command ladder, and its artifact regeneration is limited to bounded review and audit artifacts. It does not create data/manifests/reproducibility_acceptance.json, and does not support calibrated real-world or operational routing claims.

## Required Actions

- review whether the bounded clean-checkout smoke is sufficient for the intended review scope
- preserve full command-ladder logs before formal acceptance
- keep data/manifests/reproducibility_acceptance.json absent until a human reviewer records the reproduction scope
