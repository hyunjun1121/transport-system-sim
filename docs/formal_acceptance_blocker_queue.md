# Formal Decision Blocker Queue

Formal decision blocker queue only. Rows are work items for reviewers; they do not create approvals, source evidence, field-fit benchmark evidence, or deployment routing permission.

## Summary

- Queue rows: 2
- Formal decision ready: `false`
- Study-closeout ready: `false`
- Can mark complete: `false`
- CSV: `data/manifests/formal_acceptance_blocker_queue.csv`

## Queue

| Gate | Action Type | Formal Target | Review Packet | Blocker |
| --- | --- | --- | --- | --- |
| road_class_overrides | apply_reviewed_input_and_regenerate | `data/parameters/road_class_overrides.csv` | `docs/review_packets/cached_osm_input.md` | verify graph-adapter runs apply the reviewed override table before using road-calibration claims |
| final_audit_document | resolve_blocker | `docs/final_study_audit.md` | `docs/review_packets/final_audit.md` | final study audit document does not state final_study_ready true |

## Use

Work this queue from top to bottom. If evidence is missing, leave the formal target absent. If evidence exists, update the formal target with a real reviewed decision and rerun the formal decision package audits.
