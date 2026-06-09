# Artifact Invalidation Quarantine Closeout Prefill

Artifact invalidation matrix for Phase 9 preflight review only; not an artifact regeneration record, not evidence-quality validation, not publication readiness, not final-study approval, and not formal acceptance.

## Summary

- Source action batch: `quarantine_non_evidence`
- Prefill only: `true`
- Phase 9 promotion ready: `false`
- Can clear invalidation gate: `false`
- Must not be used as closeout manifest: `true`
- Rows: 6
- Prefilled rows: 6
- Candidate artifacts copied into prefill: 73
- Pending or invalid rows: 6
- CSV SHA256: `6437c2cf63724e7e84f5724ba807859256c6f3b2dcccd0dc4f22319b98eef2d5`
- Source transfer packet manifest: `data/validation/artifact_invalidation_quarantine_non_evidence_transfer_packet_manifest.json`
- Source transfer packet SHA256: `fd6f666b561e535e1ed186a58d9026fca5fa2a1c0d7a78cc552a43ce0884e90f`
- Source transfer packet status: `loaded`
- Source transfer packet row count: 6
- Source transfer packet integrity flag: `true`

## Prefill Rows

| Row Key | Actual Disposition | Status | Candidate Artifacts | Exclusion Scope | Audit | Signoff | Can Clear |
| --- | --- | --- | ---: | --- | --- | --- | --- |
| claim_boundary_or_readiness_logic->review_packages | marked_non_evidence | pending | 13 | Prefill only. Reviewer must confirm whether 13 candidate `review_packages` artifacts are stale/non-evidence for row `claim_boundary_or_readiness_logic->review_packages` and resolve 20 current claim-text references before copying this row into the main closeout record. | not_run | unsigned | false |
| demand_fleet_behavior_transfer_dispatch->full_outputs | marked_non_evidence | pending | 12 | Prefill only. Reviewer must confirm whether 12 candidate `full_outputs` artifacts are stale/non-evidence for row `demand_fleet_behavior_transfer_dispatch->full_outputs` and resolve 21 current claim-text references before copying this row into the main closeout record. | not_run | unsigned | false |
| disruption_library_or_exposure->full_outputs | marked_non_evidence | pending | 12 | Prefill only. Reviewer must confirm whether 12 candidate `full_outputs` artifacts are stale/non-evidence for row `disruption_library_or_exposure->full_outputs` and resolve 21 current claim-text references before copying this row into the main closeout record. | not_run | unsigned | false |
| rail_source_or_timing->full_outputs | marked_non_evidence | pending | 12 | Prefill only. Reviewer must confirm whether 12 candidate `full_outputs` artifacts are stale/non-evidence for row `rail_source_or_timing->full_outputs` and resolve 21 current claim-text references before copying this row into the main closeout record. | not_run | unsigned | false |
| region_boundary->full_outputs | marked_non_evidence | pending | 12 | Prefill only. Reviewer must confirm whether 12 candidate `full_outputs` artifacts are stale/non-evidence for row `region_boundary->full_outputs` and resolve 21 current claim-text references before copying this row into the main closeout record. | not_run | unsigned | false |
| road_snapshot_or_evidence->full_outputs | marked_non_evidence | pending | 12 | Prefill only. Reviewer must confirm whether 12 candidate `full_outputs` artifacts are stale/non-evidence for row `road_snapshot_or_evidence->full_outputs` and resolve 21 current claim-text references before copying this row into the main closeout record. | not_run | unsigned | false |

## Use

This file converts the quarantine transfer packet into a closeout-schema worksheet so a reviewer can copy confirmed path and hash evidence into the separate main closeout record. It is prefill only: it keeps `closeout_status=pending`, audit/test results as `not_run`, reviewer signoff as `unsigned`, and `can_clear_invalidation_gate=false`. It is not closeout evidence, not citation-removal approval, not reviewer signoff, not artifact regeneration evidence, not publication readiness, not final-study approval, not formal acceptance, and not authorization for Phase 9.
