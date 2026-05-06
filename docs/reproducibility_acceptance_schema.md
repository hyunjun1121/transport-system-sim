# Reproducibility Acceptance Schema

> Current project status (2026-05-06): `final_study_ready=false`. Ready gates are `3/15` (`real_input_smoke`, `structured_disruptions`, `policy_alternatives`), blocked gates are `12/15`, and formal acceptance is `0/12` ready. This document is current-state or review support only; it does not create formal approval, calibrated real-world results, or operational routing guidance.


## Purpose

`data/manifests/reproducibility_acceptance.json` is the explicit review record
that can close the final-study reproducibility gate.

A reproducibility manifest can list commands while still being scaffold-only.
The final gate requires a clean-checkout validation decision, validation-ladder
review, artifact-regeneration review, manifest-path review, import-boundary
check, and bounded claim language.

Do not create this file to make audits pass. Create it only after a real
clean-checkout reproduction review has accepted the package.

## Location

```text
data/manifests/reproducibility_acceptance.json
```

The current scaffold intentionally does not include this file.

## Required Fields

| Field | Type | Requirement |
| --- | --- | --- |
| `region_id` | string | Non-empty pilot region identifier. |
| `accepted` | boolean | Must be `true` only after review. |
| `accepted_by` | string | Reviewer, group, or decision record identifier. |
| `accepted_date` | string | Review date in `YYYY-MM-DD` form where possible. |
| `clean_checkout_tested` | boolean | Must be `true` after clean-checkout reproduction. |
| `validation_ladder_passed` | boolean | Must be `true` after the final validation ladder passes. |
| `artifact_regeneration_tested` | boolean | Must be `true` after required outputs regenerate. |
| `manifest_paths_reviewed` | boolean | Must be `true` after manifest paths and commands are reviewed. |
| `no_runtime_cloned_repo_imports` | boolean | Must be `true` after runtime import boundary checks. |
| `expected_validation_command_count` | integer | Positive count matching the reproducibility manifest validation command count. |
| `claim_boundary` | string | Must include `not operational`. |
| `evidence_paths` | array of strings | Non-empty list of reviewed reproduction logs, manifests, audit notes, or command records. |

## Example Shape

```json
{
  "region_id": "songpa_public_demo",
  "accepted": true,
  "accepted_by": "review record id",
  "accepted_date": "2026-05-04",
  "clean_checkout_tested": true,
  "validation_ladder_passed": true,
  "artifact_regeneration_tested": true,
  "manifest_paths_reviewed": true,
  "no_runtime_cloned_repo_imports": true,
  "expected_validation_command_count": 19,
  "claim_boundary": "Accepted for quasi-real decision-support analysis; not operational routing.",
  "evidence_paths": [
    "docs/reproducibility_package.md",
    "data/manifests/reproducibility_manifest.json",
    "docs/final_study_audit.md"
  ]
}
```

This example is a schema illustration only. It is not evidence that the current
package has passed clean-checkout final reproduction.

## Validation

The schema is enforced by:

```powershell
.\.venv\Scripts\python tests\test_realworld_reproducibility_acceptance.py
.\.venv\Scripts\python tests\test_realworld_final_study_readiness.py
.\.venv\Scripts\python scripts\audit_final_study_readiness.py
```

The final-study readiness audit also checks the accepted validation command
count against the reproducibility manifest. A stale acceptance record must keep
the reproducibility gate blocked.
