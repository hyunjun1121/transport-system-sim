# Reproducibility Review Packet

Sub-agent records are review aids. They do not replace formal acceptance artifacts, source-backed reviewer decisions, calibrated validation, or operational routing approval.

- Gate ID: `reproducibility`
- Agent: `Clean-Checkout Reproducibility Agent`
- Status: `blocked`
- Can mark complete: `false`
- Generated at: `2026-05-04T11:47:40+00:00`

## Decision

Clean-Checkout Reproducibility Agent cannot accept gate reproducibility; the current final-study readiness audit reports blockers.

## Reviewed Inputs

- docs/reproducibility_package.md
- data/manifests/reproducibility_manifest.json
- data/validation/reproducibility_review_packet.csv
- scripts/audit_plan_artifacts.py
- data/manifests/reproducibility_acceptance.json
- data/validation/reproducibility_review_manifest.json
- data/validation/reproducibility_smoke_manifest.json
- docs/reproducibility_smoke.md

## Evidence And Source Paths

- data/manifests/reproducibility_acceptance.json
- docs/reproducibility_package.md
- data/manifests/reproducibility_manifest.json
- data/validation/reproducibility_review_packet.csv
- data/validation/reproducibility_review_manifest.json
- data/validation/reproducibility_smoke_manifest.json
- docs/reproducibility_smoke.md
- docs/review_packets/reproducibility.md
- requirements.txt

## Risks

- Local dirty-tree validation can miss missing files or untracked artifacts.
- Scaffold reproducibility manifests do not prove final package reproducibility.
- create an explicit reproducibility acceptance record after clean-checkout validation, artifact regeneration, manifest review, and import-boundary checks
- replace scaffold-only manifest with clean-checkout final reproduction package

## Required Actions

- Run or document clean-checkout validation with command log and artifact regeneration evidence.
- Create reproducibility_acceptance.json only after accepted reproduction scope is complete.
- create an explicit reproducibility acceptance record after clean-checkout validation, artifact regeneration, manifest review, and import-boundary checks
- replace scaffold-only manifest with clean-checkout final reproduction package

## Formal Acceptance Boundary

To close this final-study gate, create or update the formal acceptance artifact listed in the agent definition. Do not edit this review packet as a substitute for formal acceptance.

Formal acceptance artifacts:

- data/manifests/reproducibility_acceptance.json

## Current Final-Study Gate Details

```json
{
  "artifact_present": true,
  "blockers": [
    "create an explicit reproducibility acceptance record after clean-checkout validation, artifact regeneration, manifest review, and import-boundary checks",
    "replace scaffold-only manifest with clean-checkout final reproduction package"
  ],
  "details": {
    "acceptance_path": "data/manifests/reproducibility_acceptance.json",
    "acceptance_record_present": false,
    "accepted_validation_command_count": null,
    "current_worktree_smoke_command_count": 24,
    "current_worktree_smoke_failed_count": 0,
    "current_worktree_smoke_passed": true,
    "current_worktree_smoke_present": true,
    "current_worktree_smoke_scope": "current_worktree_smoke_not_clean_checkout",
    "review_packet_clean_checkout_test_performed": false,
    "review_packet_git_status_line_count": 5,
    "review_packet_no_runtime_cloned_repo_imports": true,
    "review_packet_present": true,
    "review_packet_row_count": 7,
    "review_packet_untracked_count": 0,
    "scope": "scaffold-only real-world pilot package",
    "validation_command_count": 42
  },
  "evidence": [
    "data/manifests/reproducibility_acceptance.json",
    "docs/reproducibility_package.md",
    "data/manifests/reproducibility_manifest.json",
    "data/validation/reproducibility_review_packet.csv",
    "data/validation/reproducibility_review_manifest.json",
    "data/validation/reproducibility_smoke_manifest.json",
    "docs/reproducibility_smoke.md"
  ],
  "gate_id": "reproducibility",
  "label": "Reproducibility",
  "ready": false
}
```
