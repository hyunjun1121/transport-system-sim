# Source Context Cache Decision Packet

Source context-cache decision packet only; not source acceptance, not license certification, not cached source evidence, not provenance gate closure, and not operational routing approval. It cannot create data/manifests/provenance_acceptance.json.

## Verdict

- Publication ready: `false`
- Can mark complete: `false`
- Cache/retention/exclusion decision recorded: `false`
- Decision rows: 3
- Blocking decisions: 3
- Human-review decisions: 0
- Missing target cache artifacts: 3

## Decision Rows

| Source | Status | Options | Target Artifacts | Required Action |
| --- | --- | --- | --- | --- |
| ktdb_public_transport_gtfs_context | blocked_missing_context_source_cache_retention_or_exclusion_decision | cache_reviewed_extract; retain_as_sensitivity_or_context_only; exclude_from_release_scope_claims | data/rail/pilot_gtfs.zip; data/rail/pilot_gtfs/ | Choose whether to cache reviewed source evidence, retain this source as sensitivity/context-only, or exclude it from release-scope claims. |
| seoul_shortest_path_api_context | blocked_missing_context_source_cache_retention_or_exclusion_decision | cache_reviewed_extract; retain_as_sensitivity_or_context_only; exclude_from_release_scope_claims | data/rail/pilot_rail_shortest_path_cache.csv; data/rail/pilot_rail_shortest_path_raw.json | Choose whether to cache reviewed source evidence, retain this source as sensitivity/context-only, or exclude it from release-scope claims. |
| seoul_timetable_api_context | blocked_missing_context_source_cache_retention_or_exclusion_decision | cache_reviewed_extract; retain_as_sensitivity_or_context_only; exclude_from_release_scope_claims | data/rail/pilot_rail_timetable_cache.csv; data/rail/pilot_rail_timetable_raw.json | Choose whether to cache reviewed source evidence, retain this source as sensitivity/context-only, or exclude it from release-scope claims. |

## Boundary

- This packet is a reviewer worksheet, not a formal decision record.
- It does not cache data, certify terms, or accept source provenance.
- Keep release-scope claims blocked until retained sources are reviewed and formal provenance acceptance exists.
