# Reproducibility Review Packet

Sub-agent records are review aids. They do not replace formal acceptance artifacts, source-backed reviewer decisions, calibrated validation, or operational routing approval.

- Gate ID: `reproducibility`
- Agent: `Clean-Checkout Reproducibility Agent`
- Status: `blocked`
- Can mark complete: `false`
- Generated at: `2026-07-05T07:30:47+00:00`

## Decision

Clean-Checkout Reproducibility Agent cannot accept gate reproducibility; the current final-study readiness audit reports blockers.

## Reviewed Inputs

- docs/reproducibility_package.md
- data/manifests/reproducibility_manifest.json
- data/manifests/current_goal_completion_audit.json
- data/validation/reproducibility_review_packet.csv
- data/validation/reproducibility_decision_manifest.json
- data/validation/tracked_artifact_audit.csv
- docs/reproducibility_decision_packet.md
- scripts/audit_plan_artifacts.py
- data/manifests/reproducibility_acceptance.json
- data/validation/reproducibility_review_manifest.json
- data/validation/reproducibility_decision_packet.csv
- data/validation/reproducibility_smoke_manifest.json
- docs/reproducibility_smoke.md
- data/validation/clean_checkout_reproducibility_smoke_manifest.json
- docs/clean_checkout_reproducibility_smoke.md

## Evidence And Source Paths

- data/manifests/reproducibility_acceptance.json
- docs/reproducibility_package.md
- data/manifests/reproducibility_manifest.json
- data/validation/reproducibility_review_packet.csv
- data/validation/reproducibility_review_manifest.json
- data/validation/reproducibility_decision_packet.csv
- data/validation/reproducibility_decision_manifest.json
- docs/reproducibility_decision_packet.md
- data/validation/reproducibility_smoke_manifest.json
- docs/reproducibility_smoke.md
- data/validation/clean_checkout_reproducibility_smoke_manifest.json
- docs/clean_checkout_reproducibility_smoke.md
- data/validation/tracked_artifact_audit.csv
- docs/review_packets/reproducibility.md
- data/validation/tracked_artifact_audit_manifest.json
- data/manifests/current_goal_completion_audit.json
- requirements.txt

## Risks

- Local dirty-tree validation can miss missing files or untracked artifacts.
- Scaffold reproducibility manifests do not prove final package reproducibility.
- review reproducibility human-decision rows before reproducibility acceptance

## Required Actions

- Run or document clean-checkout validation with command log and artifact regeneration evidence.
- Create reproducibility_acceptance.json only after accepted reproduction scope is complete.
- review reproducibility human-decision rows before reproducibility acceptance

## Formal Acceptance Boundary

To close this final-study gate, create or update the formal acceptance artifact listed in the agent definition. Do not edit this review packet as a substitute for formal acceptance.

Formal acceptance artifacts:

- data/manifests/reproducibility_acceptance.json

## Current Final-Study Gate Details

```json
{
  "artifact_present": true,
  "blockers": [
    "review reproducibility human-decision rows before reproducibility acceptance"
  ],
  "details": {
    "acceptance_path": "data/manifests/reproducibility_acceptance.json",
    "acceptance_record_present": true,
    "accepted_validation_command_count": 43,
    "clean_checkout_smoke_command_count": 9,
    "clean_checkout_smoke_environment_scope": "clean_source_checkout_fresh_venv_with_dependency_install",
    "clean_checkout_smoke_failed_count": 0,
    "clean_checkout_smoke_full_clean_environment_tested": true,
    "clean_checkout_smoke_passed": true,
    "clean_checkout_smoke_present": true,
    "clean_checkout_smoke_scope": "clean_checkout_source_tree_smoke_not_formal_acceptance",
    "current_worktree_smoke_command_count": 9,
    "current_worktree_smoke_failed_count": 0,
    "current_worktree_smoke_passed": true,
    "current_worktree_smoke_present": true,
    "current_worktree_smoke_scope": "current_worktree_smoke_not_clean_checkout",
    "reproducibility_decision_blocking_decision_count": 0,
    "reproducibility_decision_can_mark_complete": false,
    "reproducibility_decision_human_review_decision_count": 7,
    "reproducibility_decision_manifest_present": true,
    "reproducibility_decision_publication_ready": false,
    "reproducibility_decision_remaining_blockers": [],
    "reproducibility_decision_row_count": 7,
    "reproducibility_decision_status_counts": {
      "needs_human_review_artifact_regeneration": 1,
      "needs_human_review_clean_checkout_evidence_scope": 1,
      "needs_human_review_command_ladder_scope": 1,
      "needs_human_review_committed_package_state": 1,
      "needs_human_review_formal_reproducibility_acceptance": 1,
      "needs_human_review_reproducibility_manifest_scope": 1,
      "needs_human_review_runtime_import_boundary": 1
    },
    "review_packet_clean_checkout_test_performed": true,
    "review_packet_git_status_line_count": 234,
    "review_packet_no_runtime_cloned_repo_imports": true,
    "review_packet_present": true,
    "review_packet_row_count": 8,
    "review_packet_untracked_count": 9,
    "scope": "Reviewer-accepted real-world pilot reproduction package within formal-acceptance claim boundary",
    "validation_command_count": 43
  },
  "evidence": [
    "data/manifests/reproducibility_acceptance.json",
    "docs/reproducibility_package.md",
    "data/manifests/reproducibility_manifest.json",
    "data/validation/reproducibility_review_packet.csv",
    "data/validation/reproducibility_review_manifest.json",
    "data/validation/reproducibility_decision_packet.csv",
    "data/validation/reproducibility_decision_manifest.json",
    "docs/reproducibility_decision_packet.md",
    "data/validation/reproducibility_smoke_manifest.json",
    "docs/reproducibility_smoke.md",
    "data/validation/clean_checkout_reproducibility_smoke_manifest.json",
    "docs/clean_checkout_reproducibility_smoke.md"
  ],
  "gate_id": "reproducibility",
  "label": "Reproducibility",
  "ready": false
}
```
