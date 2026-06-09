# Artifact Invalidation Quarantine Closeout Prefill Gap Audit

Artifact invalidation matrix for Phase 9 preflight review only; not an artifact regeneration record, not evidence-quality validation, not publication readiness, not final-study approval, and not formal acceptance.

## Summary

- Source action batch: `quarantine_non_evidence`
- Gap audit only: `true`
- Can clear invalidation gate: `false`
- Must not be used as closeout manifest: `true`
- Rows: 6
- Rows with blocking gaps: 6
- Candidate artifacts: 73
- Reference hits: 125
- CSV SHA256: `a8b436b43d5f7b909765060abb6e894bd7fa11be7f78bdf5990f6ee8b1abeda0`
- Source transfer packet manifest: `data/validation/artifact_invalidation_quarantine_non_evidence_transfer_packet_manifest.json`
- Source transfer packet SHA256: `fd6f666b561e535e1ed186a58d9026fca5fa2a1c0d7a78cc552a43ce0884e90f`
- Source transfer packet status: `loaded`

## Gap Counts

| Gap Code | Rows |
| --- | ---: |
| artifact_or_exclusion_confirmation_missing | 6 |
| audit_not_passed | 6 |
| claim_boundary_review_missing | 6 |
| closeout_status_not_closed | 6 |
| main_closeout_copy_required | 6 |
| rerun_not_passed | 6 |
| reviewer_signoff_missing | 6 |
| targeted_test_not_passed | 6 |

## Row Gaps

| Main Row | Row Key | Group | Candidates | References | Closeout Status | Gaps | Next Reviewer Action |
| ---: | --- | --- | ---: | ---: | --- | --- | --- |
| 50 | claim_boundary_or_readiness_logic->review_packages | review_packages | 13 | 20 | pending | artifact_or_exclusion_confirmation_missing, closeout_status_not_closed, rerun_not_passed, audit_not_passed, targeted_test_not_passed, claim_boundary_review_missing, reviewer_signoff_missing, main_closeout_copy_required | Confirm stale/non-evidence treatment, resolve claim-text references, run the recorded audit and targeted test, then copy the confirmed row into the main closeout record with non-acceptance reviewer signoff. |
| 22 | demand_fleet_behavior_transfer_dispatch->full_outputs | full_outputs | 12 | 21 | pending | artifact_or_exclusion_confirmation_missing, closeout_status_not_closed, rerun_not_passed, audit_not_passed, targeted_test_not_passed, claim_boundary_review_missing, reviewer_signoff_missing, main_closeout_copy_required | Confirm stale/non-evidence treatment, resolve claim-text references, run the recorded audit and targeted test, then copy the confirmed row into the main closeout record with non-acceptance reviewer signoff. |
| 30 | disruption_library_or_exposure->full_outputs | full_outputs | 12 | 21 | pending | artifact_or_exclusion_confirmation_missing, closeout_status_not_closed, rerun_not_passed, audit_not_passed, targeted_test_not_passed, claim_boundary_review_missing, reviewer_signoff_missing, main_closeout_copy_required | Confirm stale/non-evidence treatment, resolve claim-text references, run the recorded audit and targeted test, then copy the confirmed row into the main closeout record with non-acceptance reviewer signoff. |
| 18 | rail_source_or_timing->full_outputs | full_outputs | 12 | 21 | pending | artifact_or_exclusion_confirmation_missing, closeout_status_not_closed, rerun_not_passed, audit_not_passed, targeted_test_not_passed, claim_boundary_review_missing, reviewer_signoff_missing, main_closeout_copy_required | Confirm stale/non-evidence treatment, resolve claim-text references, run the recorded audit and targeted test, then copy the confirmed row into the main closeout record with non-acceptance reviewer signoff. |
| 5 | region_boundary->full_outputs | full_outputs | 12 | 21 | pending | artifact_or_exclusion_confirmation_missing, closeout_status_not_closed, rerun_not_passed, audit_not_passed, targeted_test_not_passed, claim_boundary_review_missing, reviewer_signoff_missing, main_closeout_copy_required | Confirm stale/non-evidence treatment, resolve claim-text references, run the recorded audit and targeted test, then copy the confirmed row into the main closeout record with non-acceptance reviewer signoff. |
| 12 | road_snapshot_or_evidence->full_outputs | full_outputs | 12 | 21 | pending | artifact_or_exclusion_confirmation_missing, closeout_status_not_closed, rerun_not_passed, audit_not_passed, targeted_test_not_passed, claim_boundary_review_missing, reviewer_signoff_missing, main_closeout_copy_required | Confirm stale/non-evidence treatment, resolve claim-text references, run the recorded audit and targeted test, then copy the confirmed row into the main closeout record with non-acceptance reviewer signoff. |

## Use

This gap audit is a reviewer-action checklist for the quarantine closeout prefill. It does not replace the main closeout record. It does not close artifact invalidation rows, does not approve citation removal or exclusion, does not provide reviewer signoff, does not promote Phase 9 outputs, and does not support publication or final-study claims. Confirmed evidence must be copied into the main closeout record with audit, targeted-test, and reviewer signoff fields filled.
