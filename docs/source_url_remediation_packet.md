# Source URL Remediation Packet

Source URL remediation packet only; not source acceptance, not license certification, not calibrated real-world validation, and not operational routing approval. Remediation rows identify review work only and cannot close data/manifests/provenance_acceptance.json.

## Verdict

- Publication ready: `false`
- Can mark complete: `false`
- Remediation rows: 16
- Blocking issues: 0
- Live checks still required: 12
- Status counts: `{'live_check_required': 12, 'local_citation_needs_review': 4}`

## Remediation Rows

| Source | URL Status | Remediation | Priority | Required Action |
| --- | --- | --- | --- | --- |
| osm_overpass_road_snapshot | not_checked | live_check_required | high | run the live source-URL check and then manually verify or replace the source |
| osm_overpass_road_snapshot | not_checked | live_check_required | high | run the live source-URL check and then manually verify or replace the source |
| pilot_region_spec | no_url_detected | local_citation_needs_review | medium | confirm the local citation is sufficient for project-owned input and privacy scope |
| parameter_source_tables | no_url_detected | local_citation_needs_review | medium | confirm the local citation is sufficient for project-owned input and privacy scope |
| seoul_station_binding_cache | not_checked | live_check_required | high | run the live source-URL check and then manually verify or replace the source |
| seoul_shortest_path_api_context | not_checked | live_check_required | high | run the live source-URL check and then manually verify or replace the source |
| seoul_shortest_path_api_context | not_checked | live_check_required | high | run the live source-URL check and then manually verify or replace the source |
| seoul_timetable_api_context | not_checked | live_check_required | high | run the live source-URL check and then manually verify or replace the source |
| seoul_timetable_api_context | not_checked | live_check_required | high | run the live source-URL check and then manually verify or replace the source |
| metro9_capacity_context | not_checked | live_check_required | high | run the live source-URL check and then manually verify or replace the source |
| osrm_public_route_benchmark | not_checked | live_check_required | high | run the live source-URL check and then manually verify or replace the source |
| osrm_public_route_benchmark | not_checked | live_check_required | high | run the live source-URL check and then manually verify or replace the source |
| osrm_public_route_benchmark | not_checked | live_check_required | high | run the live source-URL check and then manually verify or replace the source |
| osrm_public_route_benchmark | not_checked | live_check_required | high | run the live source-URL check and then manually verify or replace the source |
| structured_scenario_tables | no_url_detected | local_citation_needs_review | medium | confirm the local citation is sufficient for project-owned input and privacy scope |
| reproducibility_package | no_url_detected | local_citation_needs_review | medium | confirm the local citation is sufficient for project-owned input and privacy scope |

## Required Reviewer Actions

- Replace stale or unreachable public URLs with verified official sources, or exclude them from final claims.
- Confirm that local repository citations are acceptable for project-owned inputs.
- Treat `reachable` as connectivity evidence only; license and source suitability still need review.
- Create `data/manifests/provenance_acceptance.json` only after source-backed review.
