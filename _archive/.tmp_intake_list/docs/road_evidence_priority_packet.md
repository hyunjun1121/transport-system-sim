# Road Evidence Priority Packet

This packet prioritizes existing road evidence gaps by canonical route exposure. It does not create road_class_overrides.csv, does not certify source sufficiency, and does not close road, validation, graph-scale, or final-study gates.

## Verdict

- Publication ready: `false`
- Can mark complete: `false`
- Priority rows: 11
- Exposed highways: 7
- Blocking priority rows: 5
- Status counts: `{'blocked_exposed_connector_assumption': 1, 'blocked_exposed_high_priority_road_evidence_gap': 4, 'needs_review_exposed_medium_priority_road_evidence_gap': 2, 'queued_no_current_canonical_route_exposure': 4}`

## Priority Rows

| Highway | Status | Exposure Rows | Route Candidates | Time min | Max Time Share | Required Action |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| primary | blocked_exposed_high_priority_road_evidence_gap | 12 | 12 | 14.004728 | 0.490303 | prioritize reviewed or explicitly accepted speed, capacity, and disruption values for this exposed road class |
| tertiary | blocked_exposed_high_priority_road_evidence_gap | 12 | 12 | 12.325286 | 0.58369 | prioritize reviewed or explicitly accepted speed, capacity, and disruption values for this exposed road class |
| secondary | blocked_exposed_high_priority_road_evidence_gap | 14 | 14 | 11.06218 | 0.722504 | prioritize reviewed or explicitly accepted speed, capacity, and disruption values for this exposed road class |
| residential | blocked_exposed_high_priority_road_evidence_gap | 12 | 12 | 2.026716 | 0.119097 | prioritize reviewed or explicitly accepted speed, capacity, and disruption values for this exposed road class |
| connector | blocked_exposed_connector_assumption | 18 | 18 | 20.394984 | 0.402071 | review connector snapping distances, connector travel times, capacity assumptions, and zero-failure treatment before route-level claims |
| primary_link | needs_review_exposed_medium_priority_road_evidence_gap | 6 | 6 | 0.88868 | 0.075637 | review after exposed high-priority classes, or sooner if graph-scale selection makes this class claim-relevant |
| tertiary_link | needs_review_exposed_medium_priority_road_evidence_gap | 2 | 2 | 0.209012 | 0.024371 | review after exposed high-priority classes, or sooner if graph-scale selection makes this class claim-relevant |
| secondary_link | queued_no_current_canonical_route_exposure | 0 | 0 | 0 | 0 | keep this class in the road override review backlog unless graph-scale or route-candidate changes expose it |
| trunk | queued_no_current_canonical_route_exposure | 0 | 0 | 0 | 0 | keep this class in the road override review backlog unless graph-scale or route-candidate changes expose it |
| trunk_link | queued_no_current_canonical_route_exposure | 0 | 0 | 0 | 0 | keep this class in the road override review backlog unless graph-scale or route-candidate changes expose it |
| unclassified | queued_no_current_canonical_route_exposure | 0 | 0 | 0 | 0 | keep this class in the road override review backlog unless graph-scale or route-candidate changes expose it |

## Boundary

- This packet is road-evidence prioritization support only.
- It does not create reviewed overrides, source acceptance, calibration, validation, graph-scale acceptance, or operational routing evidence.
- It cannot create or replace `data/parameters/road_class_overrides.csv`.
