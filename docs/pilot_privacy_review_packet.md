# Pilot Privacy Review Packet

> Current project status (2026-05-06): `final_study_ready=false`. Ready gates are `3/15` (`real_input_smoke`, `structured_disruptions`, `policy_alternatives`), blocked gates are `12/15`, and formal acceptance is `0/12` ready. This document is current-state or review support only; it does not create formal approval, calibrated real-world results, or operational routing guidance.


Pilot privacy review packet only; not pilot acceptance, not privacy approval, not calibrated real-world validation, and not operational routing approval. A reviewer must still create data/manifests/pilot_acceptance.json before the pilot-region gate can close.

## Verdict

- Publication ready: `false`
- Can mark complete: `false`
- Review rows: 7
- Rows requiring review: 7
- Closure candidates: 0

## Review Rows

| Item | Type | Coordinate Class | Privacy Risk | Required Decision |
| --- | --- | --- | --- | --- |
| region_boundary | boundary | public_admin_or_bbox | low_pending_review | confirm bbox is acceptable public geography and not an operational area definition |
| assembly_zone:A | assembly_zone | public | low_pending_review | confirm public assembly demo point is not framed as an operational assembly order |
| destination_zone:D | destination_zone | synthetic | low_if_abstraction_accepted | confirm destination is synthetic or sufficiently generalized and cannot be read as a sensitive operational destination |
| rail_access_point:S | rail_access_point | public | low_pending_review | confirm public station point is acceptable for non-operational multimodal demonstration |
| rail_egress_point:R | rail_egress_point | public | low_pending_review | confirm public station point is acceptable for non-operational multimodal demonstration |
| coordinate_policy | policy | public_or_synthetic_points_only | policy_pending_review | confirm all retained points follow the public_or_synthetic_points_only policy |
| data_card_claim_boundary | claim_boundary | documentation | low_if_claim_boundary_accepted | confirm data card keeps the pilot non-sensitive, non-operational, and not calibrated |

## Required Reviewer Actions

- Review `data/regions/pilot_region.yaml` and `docs/pilot_region_data_card.md` together.
- Confirm that public and synthetic points are acceptable for a non-operational demo.
- Confirm whether the pilot can be cited in the manuscript before evidence gates close.
- Create `data/manifests/pilot_acceptance.json` only after a real reviewer decision.
