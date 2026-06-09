# Artifact Invalidation Quarantine Main Closeout Draft Overlay

Artifact invalidation matrix for Phase 9 preflight review only; not an artifact regeneration record, not evidence-quality validation, not publication readiness, not final-study approval, and not formal acceptance.

## Summary

- Source action batch: `quarantine_non_evidence`
- Draft overlay only: `true`
- Can clear invalidation gate: `false`
- Must not be used as closeout manifest: `true`
- Must not replace main closeout record: `true`
- Rows: 51
- Prefill rows: 6
- Overlayed rows: 6
- Closed candidates: 0
- Pending or invalid rows: 51
- CSV SHA256: `6b96631c064209ea23ed79bc13e1a2b842a5d2fe8cbe249024a86bef17d7a547`
- Source prefill: `data/validation/artifact_invalidation_quarantine_closeout_prefill.csv`
- Source main closeout: `data/validation/artifact_invalidation_closeout_template.csv`

## Disposition Counts

| Actual Disposition | Rows |
| --- | ---: |
| marked_non_evidence | 6 |
| pending | 45 |

## Overlay Rows

| Row Key | Group | Actual Disposition | Status | Candidate Artifacts | Audit | Test | Signoff | Can Clear |
| --- | --- | --- | --- | ---: | --- | --- | --- | --- |
| region_boundary->full_outputs | full_outputs | marked_non_evidence | pending | 12 | not_run | not_run | unsigned | false |
| road_snapshot_or_evidence->full_outputs | full_outputs | marked_non_evidence | pending | 12 | not_run | not_run | unsigned | false |
| rail_source_or_timing->full_outputs | full_outputs | marked_non_evidence | pending | 12 | not_run | not_run | unsigned | false |
| demand_fleet_behavior_transfer_dispatch->full_outputs | full_outputs | marked_non_evidence | pending | 12 | not_run | not_run | unsigned | false |
| disruption_library_or_exposure->full_outputs | full_outputs | marked_non_evidence | pending | 12 | not_run | not_run | unsigned | false |
| claim_boundary_or_readiness_logic->review_packages | review_packages | marked_non_evidence | pending | 13 | not_run | not_run | unsigned | false |

## Use

This file is a closeout-schema draft overlay that places the quarantine prefill rows into the same row order as the main artifact invalidation closeout record. It is intentionally non-authoritative: it keeps every row pending, every audit and targeted-test result as `not_run`, reviewer signoff as `unsigned`, and all readiness flags as false. It is not the main closeout record, not reviewer signoff, not artifact regeneration evidence, not publication readiness, not final-study approval, not formal acceptance, and not Phase 9 readiness.
