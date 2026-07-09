# Road Evidence Priority Packet

This packet prioritizes existing road evidence gaps by canonical route exposure. It does not create road_class_overrides.csv, does not certify source sufficiency, and does not close road, validation, graph-scale, or final-study gates.

## Verdict

- Publication ready: `false`
- Can mark complete: `false`
- Priority rows: 11
- Exposed highways: 7
- Blocking priority rows: 1
- Status counts: `{'blocked_exposed_connector_assumption': 1, 'needs_review_exposed_medium_priority_road_evidence_gap': 6, 'queued_no_current_canonical_route_exposure': 4}`

## Priority Rows

| Highway | Status | Exposure Rows | Route Candidates | Time min | Max Time Share | Required Action |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| connector | blocked_exposed_connector_assumption | 18 | 18 | 20.394984 | 0.357065 | review connector snapping distances, connector travel times, capacity assumptions, and zero-failure treatment before route-level claims |
| primary | needs_review_exposed_medium_priority_road_evidence_gap | 12 | 12 | 16.805672 | 0.522917 | review after exposed high-priority classes, or sooner if graph-scale selection makes this class claim-relevant |
| tertiary | needs_review_exposed_medium_priority_road_evidence_gap | 12 | 12 | 16.433714 | 0.634218 | review after exposed high-priority classes, or sooner if graph-scale selection makes this class claim-relevant |
| secondary | needs_review_exposed_medium_priority_road_evidence_gap | 14 | 14 | 13.82773 | 0.734715 | review after exposed high-priority classes, or sooner if graph-scale selection makes this class claim-relevant |
| residential | needs_review_exposed_medium_priority_road_evidence_gap | 12 | 12 | 1.638994 | 0.097149 | review after exposed high-priority classes, or sooner if graph-scale selection makes this class claim-relevant |
| primary_link | needs_review_exposed_medium_priority_road_evidence_gap | 6 | 6 | 1.142592 | 0.079272 | review after exposed high-priority classes, or sooner if graph-scale selection makes this class claim-relevant |
| tertiary_link | needs_review_exposed_medium_priority_road_evidence_gap | 2 | 2 | 0.292616 | 0.028936 | review after exposed high-priority classes, or sooner if graph-scale selection makes this class claim-relevant |
| secondary_link | queued_no_current_canonical_route_exposure | 0 | 0 | 0 | 0 | keep this class in the road override review backlog unless graph-scale or route-candidate changes expose it |
| trunk | queued_no_current_canonical_route_exposure | 0 | 0 | 0 | 0 | keep this class in the road override review backlog unless graph-scale or route-candidate changes expose it |
| trunk_link | queued_no_current_canonical_route_exposure | 0 | 0 | 0 | 0 | keep this class in the road override review backlog unless graph-scale or route-candidate changes expose it |
| unclassified | queued_no_current_canonical_route_exposure | 0 | 0 | 0 | 0 | keep this class in the road override review backlog unless graph-scale or route-candidate changes expose it |

## Boundary

- This packet is road-evidence prioritization support only.
- It does not create reviewed overrides, source acceptance, calibration, validation, graph-scale acceptance, or operational routing evidence.
- It cannot create or replace `data/parameters/road_class_overrides.csv`.
