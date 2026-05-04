# Source URL Remediation Packet

Source URL remediation packet only; not source acceptance, not license certification, not calibrated real-world validation, and not operational routing approval. Remediation rows identify review work only and cannot close data/manifests/provenance_acceptance.json.

## Verdict

- Publication ready: `false`
- Can mark complete: `false`
- Remediation rows: 13
- Blocking issues: 2
- Live checks still required: 0
- Status counts: `{'blocked_unreachable_or_http_error': 2, 'local_citation_needs_review': 4, 'reachable_needs_license_review': 7}`

## Remediation Rows

| Source | URL Status | Remediation | Priority | Required Action |
| --- | --- | --- | --- | --- |
| osm_overpass_road_snapshot | reachable | reachable_needs_license_review | medium | verify source identity, terms, attribution, and retained-snapshot policy before acceptance |
| osm_overpass_road_snapshot | reachable | reachable_needs_license_review | medium | verify source identity, terms, attribution, and retained-snapshot policy before acceptance |
| pilot_region_spec | no_url_detected | local_citation_needs_review | medium | confirm the local citation is sufficient for project-owned input and privacy scope |
| parameter_source_tables | no_url_detected | local_citation_needs_review | medium | confirm the local citation is sufficient for project-owned input and privacy scope |
| seoul_station_binding_cache | reachable | reachable_needs_license_review | medium | verify source identity, terms, attribution, and retained-snapshot policy before acceptance |
| seoul_shortest_path_api_context | reachable | reachable_needs_license_review | medium | verify source identity, terms, attribution, and retained-snapshot policy before acceptance |
| seoul_shortest_path_api_context | network_error | blocked_unreachable_or_http_error | high | manually verify the URL, replace stale links, cache retained extracts, or exclude the source from final claims |
| seoul_timetable_api_context | reachable | reachable_needs_license_review | medium | verify source identity, terms, attribution, and retained-snapshot policy before acceptance |
| seoul_timetable_api_context | reachable | reachable_needs_license_review | medium | verify source identity, terms, attribution, and retained-snapshot policy before acceptance |
| metro9_capacity_context | reachable | reachable_needs_license_review | medium | verify source identity, terms, attribution, and retained-snapshot policy before acceptance |
| osrm_public_route_benchmark | http_error | blocked_unreachable_or_http_error | high | manually verify the URL, replace stale links, cache retained extracts, or exclude the source from final claims |
| structured_scenario_tables | no_url_detected | local_citation_needs_review | medium | confirm the local citation is sufficient for project-owned input and privacy scope |
| reproducibility_package | no_url_detected | local_citation_needs_review | medium | confirm the local citation is sufficient for project-owned input and privacy scope |

## Required Reviewer Actions

- Replace stale or unreachable public URLs with verified official sources, or exclude them from final claims.
- Confirm that local repository citations are acceptable for project-owned inputs.
- Treat `reachable` as connectivity evidence only; license and source suitability still need review.
- Create `data/manifests/provenance_acceptance.json` only after source-backed review.
