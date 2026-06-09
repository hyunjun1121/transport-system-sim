# Artifact Invalidation Quarantine Main Closeout Copy Audit

Artifact invalidation matrix for Phase 9 preflight review only; not an artifact regeneration record, not evidence-quality validation, not publication readiness, not final-study approval, and not formal acceptance.

## Summary

- Source action batch: `quarantine_non_evidence`
- Copy audit only: `true`
- Can clear invalidation gate: `false`
- Must not be used as closeout manifest: `true`
- Rows: 6
- Main rows found: 6
- Affected artifact fields copied: 6
- Exclusion-scope fields copied: 6
- Actual-disposition fields copied: 6
- Closed candidates: 6
- Blocking copy-audit rows: 0
- CSV SHA256: `6ee2913c66f104ef6b21bf090619dfe3f8e16ac1fd3d22236bd637971c3f0d84`
- Source prefill: `data/validation/artifact_invalidation_quarantine_closeout_prefill.csv`
- Source main closeout: `data/validation/artifact_invalidation_closeout_template.csv`

## Blocker Counts

| Blocker Code | Rows |
| --- | ---: |

## Row Copy State

| Main Row | Row Key | Group | Main Found | Artifacts | Scope | Disposition | Main Status | Gaps | Next Action |
| ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 50 | claim_boundary_or_readiness_logic->review_packages | review_packages | true | copied | copied | copied | closed_invalidation_only |  | Copy only reviewer-confirmed quarantine evidence into the main closeout row, fill audit/test/signoff fields there, then rerun the main closeout support audit. |
| 22 | demand_fleet_behavior_transfer_dispatch->full_outputs | full_outputs | true | copied | copied | copied | closed_invalidation_only |  | Copy only reviewer-confirmed quarantine evidence into the main closeout row, fill audit/test/signoff fields there, then rerun the main closeout support audit. |
| 30 | disruption_library_or_exposure->full_outputs | full_outputs | true | copied | copied | copied | closed_invalidation_only |  | Copy only reviewer-confirmed quarantine evidence into the main closeout row, fill audit/test/signoff fields there, then rerun the main closeout support audit. |
| 18 | rail_source_or_timing->full_outputs | full_outputs | true | copied | copied | copied | closed_invalidation_only |  | Copy only reviewer-confirmed quarantine evidence into the main closeout row, fill audit/test/signoff fields there, then rerun the main closeout support audit. |
| 5 | region_boundary->full_outputs | full_outputs | true | copied | copied | copied | closed_invalidation_only |  | Copy only reviewer-confirmed quarantine evidence into the main closeout row, fill audit/test/signoff fields there, then rerun the main closeout support audit. |
| 12 | road_snapshot_or_evidence->full_outputs | full_outputs | true | copied | copied | copied | closed_invalidation_only |  | Copy only reviewer-confirmed quarantine evidence into the main closeout row, fill audit/test/signoff fields there, then rerun the main closeout support audit. |

## Use

This copy audit checks whether the quarantine prefill rows have been copied into the separate main closeout record. It is not the main closeout record and does not close any invalidation row. Even a copied row remains blocked unless the main closeout row also has reviewer-confirmed disposition, audit evidence, targeted-test evidence, claim-boundary review, and non-acceptance reviewer signoff, followed by a passing main closeout support audit.
