# Source And License Review Packet

Source/license review packet only; not source acceptance, not license certification, not calibrated real-world validation, and not operational routing approval. A reviewer must still create data/manifests/provenance_acceptance.json from source-backed decisions before the provenance gate can close.

## Verdict

- Publication ready: `false`
- Can mark complete: `false`
- Source rows: 11
- Rows requiring review: 11
- Closure candidates: 0

## Source Review Rows

| Source | Status | Snapshot | Required Decision | Provenance Gate Support |
| --- | --- | --- | --- | --- |
| osm_overpass_road_snapshot | cached_snapshot_pending_review | local_artifacts_present | review source terms, attribution, snapshot date, and retained local artifacts | `false` |
| pilot_region_spec | repository_input_pending_review | local_artifacts_present | review project-owned assumptions, privacy abstraction, and claim boundary | `false` |
| parameter_source_tables | repository_input_pending_review | local_artifacts_present | review project-owned assumptions, privacy abstraction, and claim boundary | `false` |
| seoul_station_binding_cache | cached_snapshot_pending_review | local_artifacts_present | review source terms, attribution, snapshot date, and retained local artifacts | `false` |
| seoul_shortest_path_api_context | context_only_not_cached | context_only_not_cached | provide a reviewed target payload with terms/attribution review, retain this context-source row as sensitivity/context-only, or exclude it from final-study claims | `false` |
| seoul_timetable_api_context | context_only_not_cached | context_only_not_cached | provide a reviewed target payload with terms/attribution review, retain this context-source row as sensitivity/context-only, or exclude it from final-study claims | `false` |
| ktdb_public_transport_gtfs_context | cached_snapshot_pending_review | local_artifacts_present | review source terms, attribution, snapshot date, and retained local artifacts | `false` |
| metro9_capacity_context | cached_snapshot_pending_review | local_artifacts_present | review source terms, attribution, snapshot date, and retained local artifacts | `false` |
| osrm_public_route_benchmark | cached_snapshot_pending_review | local_artifacts_present | review source terms, attribution, snapshot date, and retained local artifacts | `false` |
| structured_scenario_tables | repository_input_pending_review | local_artifacts_present | review project-owned assumptions, privacy abstraction, and claim boundary | `false` |
| reproducibility_package | repository_input_pending_review | local_artifacts_present | review project-owned assumptions, privacy abstraction, and claim boundary | `false` |

## Required Reviewer Actions

- Review official source terms and attribution requirements for every retained public source.
- Provide reviewed target payloads, retain context-source rows as sensitivity/context-only evidence, or exclude them before release-scope claims.
- Confirm project-owned synthetic/privacy abstractions before retaining the pilot package.
- Create `data/manifests/provenance_acceptance.json` only after source-backed review.
