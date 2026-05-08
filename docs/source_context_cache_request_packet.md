# Source Context Cache Request Packet

This packet converts context-only public sources into cache or exclusion requests. It does not fetch data, certify terms, create source snapshots, or close data-provenance, rail-evidence, validation, reproducibility, or final-study gates.

## Verdict

- Publication ready: `false`
- Can mark complete: `false`
- Context source requests: 4
- Blocking requests: 4
- Missing target cache artifacts: 4

## Cache Requests

| Source | Status | Target Cache Artifacts | Helpers | Required Action |
| --- | --- | --- | --- | --- |
| ktdb_public_transport_gtfs_context | blocked_missing_context_source_cache | data/rail/pilot_gtfs.zip; data/rail/pilot_gtfs/ | scripts/derive_rail_gtfs_evidence.py; docs/rail_gtfs_cache_schema.md | provide reviewed KTDB or equivalent GTFS zip/directory with license and attribution review, derive rail timing evidence, or exclude this source |
| metro9_capacity_context | blocked_missing_context_source_cache | data/rail/metro9_capacity_source_extract.csv; data/rail/metro9_capacity_source_raw.html | data/parameters/rail_assumptions.csv; data/parameters/rail_service_evidence.csv | cache a reviewed operator capacity extract or explicitly retain rail capacity as sensitivity-only within the final claim boundary |
| seoul_shortest_path_api_context | blocked_missing_context_source_cache | data/rail/pilot_rail_shortest_path_cache.csv; data/rail/pilot_rail_shortest_path_raw.json | scripts/fetch_rail_shortest_path_cache.py; scripts/derive_rail_shortest_path_evidence.py; docs/rail_shortest_path_cache_schema.md | provide DATA_GO_KR_KEY or reviewed cached API payload, retain raw response, derive travel-time evidence, or exclude this source |
| seoul_timetable_api_context | blocked_missing_context_source_cache | data/rail/pilot_rail_timetable_cache.csv; data/rail/pilot_rail_timetable_raw.json | scripts/fetch_rail_timetable_cache.py; scripts/derive_rail_service_evidence.py; scripts/derive_rail_headway_evidence.py; docs/rail_timetable_cache_schema.md | provide DATA_GO_KR_KEY or reviewed cached timetable payload, retain raw response, derive headway/travel-time evidence, or exclude this source |

## Required Reviewer Actions

- Cache reviewed source extracts or explicitly exclude each context-only source from final claims.
- Review terms, attribution, extraction date, retained raw response, and reproducibility before using a cached source.
- Treat helper scripts as derivation paths only; they do not prove source suitability or close acceptance gates.
- Create `data/manifests/provenance_acceptance.json` only after source-backed review.
