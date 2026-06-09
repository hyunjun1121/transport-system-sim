# Artifact Invalidation Quarantine Non-Evidence Transfer Packet

Artifact invalidation matrix for Phase 9 preflight review only; not an artifact regeneration record, not evidence-quality validation, not publication readiness, not final-study approval, and not formal acceptance.

## Summary

- Source action batch: `quarantine_non_evidence`
- Phase 9 promotion ready: `false`
- Can clear invalidation gate: `false`
- Rows: 6
- Candidate artifacts: 73
- Candidate artifact hash matches: 73
- Candidate artifact missing: 0
- Candidate artifact hash mismatches: 0
- Current reference hits: 129
- Source integrity check: `pass`
- Covered quarantine rows: 6 / 6
- Must not be used as closeout manifest: `true`

## Transfer Rows

| Row Key | Group | Candidates | Current References | Source Scopes | Reviewer Action |
| --- | --- | ---: | ---: | --- | --- |
| demand_fleet_behavior_transfer_dispatch->full_outputs | full_outputs | 12 | 22 | ["claim_text_reference", "full_run_outputs", "full_statistics_tables", "multi_corridor_full_outputs"] | Confirm stale/non-evidence treatment, copy confirmed paths and hashes into the separate main closeout record, run citation-removal or exclusion audit, and sign off only for invalidation closeout. |
| disruption_library_or_exposure->full_outputs | full_outputs | 12 | 22 | ["claim_text_reference", "full_run_outputs", "full_statistics_tables", "multi_corridor_full_outputs"] | Confirm stale/non-evidence treatment, copy confirmed paths and hashes into the separate main closeout record, run citation-removal or exclusion audit, and sign off only for invalidation closeout. |
| rail_source_or_timing->full_outputs | full_outputs | 12 | 22 | ["claim_text_reference", "full_run_outputs", "full_statistics_tables", "multi_corridor_full_outputs"] | Confirm stale/non-evidence treatment, copy confirmed paths and hashes into the separate main closeout record, run citation-removal or exclusion audit, and sign off only for invalidation closeout. |
| region_boundary->full_outputs | full_outputs | 12 | 22 | ["claim_text_reference", "full_run_outputs", "full_statistics_tables", "multi_corridor_full_outputs"] | Confirm stale/non-evidence treatment, copy confirmed paths and hashes into the separate main closeout record, run citation-removal or exclusion audit, and sign off only for invalidation closeout. |
| road_snapshot_or_evidence->full_outputs | full_outputs | 12 | 22 | ["claim_text_reference", "full_run_outputs", "full_statistics_tables", "multi_corridor_full_outputs"] | Confirm stale/non-evidence treatment, copy confirmed paths and hashes into the separate main closeout record, run citation-removal or exclusion audit, and sign off only for invalidation closeout. |
| claim_boundary_or_readiness_logic->review_packages | review_packages | 13 | 19 | ["claim_text_reference", "expected_review_zip", "review_package_docs", "review_package_handoff", "review_package_manifest", "review_package_zip"] | Confirm stale/non-evidence treatment, copy confirmed paths and hashes into the separate main closeout record, run citation-removal or exclusion audit, and sign off only for invalidation closeout. |

## Use

This packet is reviewer triage only for the immediate `quarantine_non_evidence` batch. It is not closeout evidence, not reviewer signoff, not citation-removal approval, not artifact regeneration evidence, not transfer calibration, not publication readiness, not final-study approval, not formal acceptance, and not Phase 9 readiness. It covers only stale full-output and review-package quarantine rows, not all transfer-profile invalidation rows. Confirmed entries must be copied into the separate main artifact invalidation closeout record with audit/test evidence and non-acceptance reviewer signoff.
