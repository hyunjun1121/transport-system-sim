# Source Provenance Priority Packet

This packet prioritizes existing source provenance review work. It does not create provenance_acceptance.json, certify license compatibility, accept source snapshots, or close provenance, validation, reproducibility, or final-study gates.

## Verdict

- Publication ready: `false`
- Can mark complete: `false`
- Priority rows: 11
- Blocking sources: 4
- Human-review sources: 7
- Priority status counts: `{'blocked_context_only_source_not_cached': 4, 'needs_human_review_cached_snapshot_source': 3, 'needs_human_review_repository_input_source': 4}`

## Priority Rows

| Source | Type | Status | Priority | URLs | Required Decision |
| --- | --- | --- | --- | --- | --- |
| metro9_capacity_context | operator_page | blocked_context_only_source_not_cached | high | reachable_needs_license_review=1 | cache a reproducible source extract with terms/attribution review, or exclude this context-only source from final-study claims |
| seoul_shortest_path_api_context | public_api | blocked_context_only_source_not_cached | high | reachable_needs_license_review=2 | cache a reproducible source extract with terms/attribution review, or exclude this context-only source from final-study claims |
| seoul_timetable_api_context | public_api | blocked_context_only_source_not_cached | high | reachable_needs_license_review=2 | cache a reproducible source extract with terms/attribution review, or exclude this context-only source from final-study claims |
| ktdb_public_transport_gtfs_context | public_data | blocked_context_only_source_not_cached | high | alternate_reachable_url_needs_review=1; reachable_needs_license_review=1 | cache a reproducible source extract with terms/attribution review, or exclude this context-only source from final-study claims |
| seoul_station_binding_cache | public_api | needs_human_review_cached_snapshot_source | high | reachable_needs_license_review=1 | review source terms, attribution, snapshot date, and retained local artifacts |
| osm_overpass_road_snapshot | public_map | needs_human_review_cached_snapshot_source | high | reachable_needs_license_review=2 | review source terms, attribution, snapshot date, and retained local artifacts |
| osrm_public_route_benchmark | public_router | needs_human_review_cached_snapshot_source | high | reachable_needs_license_review=3 | review source terms, attribution, snapshot date, and retained local artifacts |
| parameter_source_tables | repository_input | needs_human_review_repository_input_source | medium | local_citation_needs_review=1 | review project-owned assumptions, privacy abstraction, and claim boundary |
| pilot_region_spec | repository_input | needs_human_review_repository_input_source | medium | local_citation_needs_review=1 | review project-owned assumptions, privacy abstraction, and claim boundary |
| reproducibility_package | repository_input | needs_human_review_repository_input_source | medium | local_citation_needs_review=1 | review project-owned assumptions, privacy abstraction, and claim boundary |
| structured_scenario_tables | repository_input | needs_human_review_repository_input_source | medium | local_citation_needs_review=1 | review project-owned assumptions, privacy abstraction, and claim boundary |

## Boundary

- This packet is source-provenance prioritization support only.
- It does not certify source terms, license compatibility, or snapshot suitability.
- It cannot create or replace `data/manifests/provenance_acceptance.json`.
