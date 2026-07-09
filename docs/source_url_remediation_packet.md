# Source URL Remediation Packet

Source URL remediation packet only; it does not certify sources, licenses, field-fit benchmark evidence, or deployment routing evidence. Remediation rows identify review work only and cannot close data/manifests/provenance_acceptance.json.

## Verdict

- Publication ready: `false`
- Can mark complete: `false`
- Remediation rows: 17
- Blocking issues: 0
- Live checks still required: 0
- Status counts: `{'alternate_reachable_url_needs_review': 1, 'local_citation_needs_review': 4, 'reachable_needs_license_review': 12}`

## Remediation Rows

| Source | URL Status | Remediation | Alternate Candidates | Local Artifacts | Priority | Required Action |
| --- | --- | --- | --- | ---: | --- | --- |
| osm_overpass_road_snapshot | reachable | reachable_needs_license_review |  | 6 | medium | verify source identity, terms, attribution, and retained-snapshot policy before provenance decision record |
| osm_overpass_road_snapshot | reachable | reachable_needs_license_review |  | 6 | medium | verify source identity, terms, attribution, and retained-snapshot policy before provenance decision record |
| pilot_region_spec | no_url_detected | local_citation_needs_review |  | 2 | medium | confirm the local citation is sufficient for project-owned input and privacy scope |
| parameter_source_tables | no_url_detected | local_citation_needs_review |  | 18 | medium | confirm the local citation is sufficient for project-owned input and privacy scope |
| seoul_station_binding_cache | reachable | reachable_needs_license_review |  | 2 | medium | verify source identity, terms, attribution, and retained-snapshot policy before provenance decision record |
| seoul_shortest_path_api_context | reachable | reachable_needs_license_review |  | 3 | medium | verify source identity, terms, attribution, and retained-snapshot policy before provenance decision record |
| seoul_shortest_path_api_context | network_error | alternate_reachable_url_needs_review | https://data.seoul.go.kr/dataList/OA-22724/A/1/datasetView.do | 3 | medium | verify whether the reachable URL and retained local artifacts are sufficient, then replace or remove the failed alternate citation before provenance decision record |
| seoul_timetable_api_context | reachable | reachable_needs_license_review |  | 4 | medium | verify source identity, terms, attribution, and retained-snapshot policy before provenance decision record |
| seoul_timetable_api_context | reachable | reachable_needs_license_review |  | 4 | medium | verify source identity, terms, attribution, and retained-snapshot policy before provenance decision record |
| ktdb_public_transport_gtfs_context | reachable | reachable_needs_license_review |  | 11 | medium | verify source identity, terms, attribution, and retained-snapshot policy before provenance decision record |
| ktdb_public_transport_gtfs_context | reachable | reachable_needs_license_review |  | 11 | medium | verify source identity, terms, attribution, and retained-snapshot policy before provenance decision record |
| metro9_capacity_context | reachable | reachable_needs_license_review |  | 4 | medium | verify source identity, terms, attribution, and retained-snapshot policy before provenance decision record |
| osrm_public_route_benchmark | reachable | reachable_needs_license_review |  | 6 | medium | verify source identity, terms, attribution, and retained-snapshot policy before provenance decision record |
| osrm_public_route_benchmark | reachable | reachable_needs_license_review |  | 6 | medium | verify source identity, terms, attribution, and retained-snapshot policy before provenance decision record |
| osrm_public_route_benchmark | reachable | reachable_needs_license_review |  | 6 | medium | verify source identity, terms, attribution, and retained-snapshot policy before provenance decision record |
| structured_scenario_tables | no_url_detected | local_citation_needs_review |  | 6 | medium | confirm the local citation is sufficient for project-owned input and privacy scope |
| reproducibility_package | no_url_detected | local_citation_needs_review |  | 6 | medium | confirm the local citation is sufficient for project-owned input and privacy scope |

## Required Reviewer Actions

- Replace stale or unreachable public URLs with verified official sources, retain them as sensitivity/context-only evidence, or exclude them from release-scope claims.
- Confirm that local repository citations are acceptable for project-owned inputs.
- Treat `reachable` as connectivity evidence only; license and source suitability still need review.
- Create `data/manifests/provenance_acceptance.json` only after source-backed review.
