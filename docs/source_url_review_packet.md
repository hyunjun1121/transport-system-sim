# Source URL Review Packet

Source URL review packet only; not source acceptance, not license certification, not calibrated real-world validation, and not operational routing approval. URL reachability is only a reviewer aid and cannot close data/manifests/provenance_acceptance.json.

## Verdict

- Publication ready: `false`
- Can mark complete: `false`
- URL rows: 13
- Live check performed: `false`
- URL statuses: `{'no_url_detected': 4, 'not_checked': 9}`

## URL Review Rows

| Source | URL | Status | HTTP | Required Boundary |
| --- | --- | --- | --- | --- |
| osm_overpass_road_snapshot | https://www.openstreetmap.org/copyright | not_checked |  | Source URL review packet only; not source acceptance, not license certification, not calibrated real-world validation, and not operational routing approval. |
| osm_overpass_road_snapshot | https://overpass-api.de/ | not_checked |  | Source URL review packet only; not source acceptance, not license certification, not calibrated real-world validation, and not operational routing approval. |
| pilot_region_spec |  | no_url_detected |  | Source URL review packet only; not source acceptance, not license certification, not calibrated real-world validation, and not operational routing approval. |
| parameter_source_tables |  | no_url_detected |  | Source URL review packet only; not source acceptance, not license certification, not calibrated real-world validation, and not operational routing approval. |
| seoul_station_binding_cache | https://data.seoul.go.kr/dataList/OA-121/S/1/datasetView.do | not_checked |  | Source URL review packet only; not source acceptance, not license certification, not calibrated real-world validation, and not operational routing approval. |
| seoul_shortest_path_api_context | https://data.seoul.go.kr/dataList/OA-22724/A/1/datasetView.do | not_checked |  | Source URL review packet only; not source acceptance, not license certification, not calibrated real-world validation, and not operational routing approval. |
| seoul_shortest_path_api_context | https://www.data.go.kr/en/data/15143842/openapi.do | not_checked |  | Source URL review packet only; not source acceptance, not license certification, not calibrated real-world validation, and not operational routing approval. |
| seoul_timetable_api_context | https://data.seoul.go.kr/dataList/32/literacyView.do | not_checked |  | Source URL review packet only; not source acceptance, not license certification, not calibrated real-world validation, and not operational routing approval. |
| seoul_timetable_api_context | https://www.data.go.kr/en/data/15143847/openapi.do | not_checked |  | Source URL review packet only; not source acceptance, not license certification, not calibrated real-world validation, and not operational routing approval. |
| metro9_capacity_context | https://www.metro9.co.kr/eng/sub03_02_01.do | not_checked |  | Source URL review packet only; not source acceptance, not license certification, not calibrated real-world validation, and not operational routing approval. |
| osrm_public_route_benchmark | https://router.project-osrm.org | not_checked |  | Source URL review packet only; not source acceptance, not license certification, not calibrated real-world validation, and not operational routing approval. |
| structured_scenario_tables |  | no_url_detected |  | Source URL review packet only; not source acceptance, not license certification, not calibrated real-world validation, and not operational routing approval. |
| reproducibility_package |  | no_url_detected |  | Source URL review packet only; not source acceptance, not license certification, not calibrated real-world validation, and not operational routing approval. |

## Required Reviewer Actions

- Verify the official source page, license, attribution, and derivative-use constraints.
- Cache retained public data extracts or explicitly exclude context-only URLs from final claims.
- Treat `reachable` as a transient connectivity observation, not acceptance evidence.
- Create `data/manifests/provenance_acceptance.json` only after source-backed review.
