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
- Full clean environment tested: `false`
- Source commit: `2be0bbe0fbca879d345f0a5a16f5d3741c21950b`
- Environment scope: `clean_source_checkout_current_python_environment`
- Can mark complete: `false`

## Outer Steps

| Step | Status | Return Code |
| --- | --- | --- |
| git_clone_source_tree | passed | 0 |
| git_checkout_source_commit | passed | 0 |
| run_reproducibility_smoke_in_clean_checkout | passed | 0 |

## Inner Smoke

- Inner scope: `current_worktree_smoke_not_clean_checkout`
- Failed commands: ``

## Claim Boundary

This is bounded clean source-checkout smoke evidence. It tests the committed source tree in a fresh clone using the current Python environment, but it does not reinstall dependencies, does not execute the full validation ladder or artifact-regeneration acceptance protocol, does not create data/manifests/reproducibility_acceptance.json, and does not support calibrated real-world or operational routing claims.

## Required Actions

- review whether current-Python clean-checkout smoke is sufficient for the intended acceptance scope
- run a full clean-environment reproduction with dependency installation if publication acceptance requires it
- preserve full validation-ladder and artifact-regeneration logs before formal acceptance
- keep data/manifests/reproducibility_acceptance.json absent until a human reviewer accepts the reproduction scope
