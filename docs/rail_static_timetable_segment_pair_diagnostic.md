# Rail Static Timetable Segment-Pair Diagnostic

Static timetable segment-pair diagnostic only; not rail-service evidence, not observed transfer calibration, not source/provenance acceptance, not license certification, not operational routing, not publication readiness, not final-study readiness, and not formal acceptance.

## Verdict

- Diagnostic only: `true`
- Publication ready: `false`
- Final-study ready: `false`
- Can support rail evidence gate: `false`
- Source: `data/rail/pilot_rail_timetable_static_source.csv`
- Source SHA256: `46b6d9e2c2e1e23632fa72208a3ca5dc6aeba9013c403ee6f52747fec2b9a9e2`
- Assumed transfer buffer: `5.0` minutes
- Feasible diagnostic connections: `240`

## Rows

| Type | Segment | Trips | Median segment | Feasible connections | Median total | Notes |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| segment | line9_olympic_park_to_seokchon | 241 | 5.917 |  |  | Same-train station-to-station segment timing from static timetable rows. |
| segment | line8_seokchon_to_jamsil | 160 | 1.833 |  |  | Same-train station-to-station segment timing from static timetable rows. |
| segment_pair_with_assumed_transfer_buffer | line9_olympic_park_to_seokchon+line8_seokchon_to_jamsil |  |  | 240 | 16.25 | Connection diagnostic uses an assumed transfer buffer only; it is not observed transfer walking, circulation, crowding, or calibration evidence. |

## Remaining Blockers

- Seokchon transfer walking, wait, circulation, and crowding are not source-backed or observed.
- Rail source decisions remain pending for source-backed timing evidence.
- This diagnostic does not validate rail capacity or emergency rail availability.
- Formal source/provenance and license acceptance remain absent.
