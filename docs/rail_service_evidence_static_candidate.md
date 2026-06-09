# Rail Service Static Timetable Candidate

Static timetable rail-service candidate only; not rail_service_evidence.csv, not rail evidence gate closure, not source/provenance acceptance, not observed transfer calibration, not publication readiness, not final-study readiness, and not formal acceptance. It can support reviewer triage only.

## Verdict

- Publication ready: `false`
- Final study ready: `false`
- Can support rail evidence gate: `false`
- Formal target written: `false`
- Rows: 1

## Candidate Rows

| Candidate | Access | Egress | Headway | Travel time | Capacity | Transfer treatment |
| --- | --- | --- | ---: | ---: | ---: | --- |
| songpa_static_timetable_segment_pair_candidate_v1 | 올림픽공원 | 잠실 | 3.583 | 16.25 | 500 | includes assumed Seokchon transfer buffer; not observed walking, platform circulation, crowding, or transfer calibration |

## Source Constraints

- Headway is a static timetable candidate, not an accepted rail evidence row.
- Travel time comes from a segment-pair diagnostic that includes an assumed transfer buffer.
- Capacity remains sensitivity-only.
- Do not use this candidate as `data/parameters/rail_service_evidence.csv` without formal source decisions.
