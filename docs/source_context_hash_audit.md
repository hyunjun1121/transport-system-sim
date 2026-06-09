# Source Context Hash Audit

This manifest proves only that retained source-context review extracts match their cached raw byte payloads. It does not prove license rights, GTFS validity, transit service calibration, source provenance acceptance, or final-study readiness.

## Verdict

- Raw-file integrity ready: `true`
- Publication ready: `false`
- Can mark complete: `false`
- Source-context rows: 2
- Raw files checked: 3
- Integrity-ready rows: 2
- Integrity blockers: 0
- Can support rail evidence gate: `false`
- Can support final provenance gate: `false`

## Source Hash Checks

| Source | Raw Payload | Recorded SHA256 | Computed SHA256 | Match |
| --- | --- | --- | --- | --- |
| ktdb_gtfs_source_context | data/rail/ktdb_gtfs_notice_raw.html | 316948d3df9ce8e0c5edaa70374584b33423b40b1e5c810b9542f8353b9ca26f | 316948d3df9ce8e0c5edaa70374584b33423b40b1e5c810b9542f8353b9ca26f | True |
| ktdb_gtfs_source_context | data/rail/ktdb_gtfs_dataset_list_raw.html | 8dacf895e039a72b04fc05434522c25946743cf0d37e99bf1b152bd9c4eb099a | 8dacf895e039a72b04fc05434522c25946743cf0d37e99bf1b152bd9c4eb099a | True |
| metro9_capacity_source_context | data/rail/metro9_capacity_source_raw.html | 712814e1a915c9a17fda4ed3aa6ab8dbb33eb29dd6146d8e4d0fd6b63b3becd5 | 712814e1a915c9a17fda4ed3aa6ab8dbb33eb29dd6146d8e4d0fd6b63b3becd5 | True |

## Boundary

- This audit checks cached raw-file hash integrity only.
- It does not validate GTFS structure, rail timetable timing, source license, or operator capacity acceptance.
- Keep provenance, rail evidence, publication, final-study, and formal acceptance gates blocked until reviewed evidence exists.
