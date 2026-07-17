# Rail Shortest-Path Cache Schema

> Current project status (2026-05-08): `final_study_ready=false`. Ready gates are `3/15` (`real_input_smoke`, `structured_disruptions`, `policy_alternatives`), blocked gates are `12/15`, and formal acceptance is `0/12` ready. This document is current-state or review support only; it does not create formal approval, calibrated real-world results, or operational routing guidance.


This schema defines the local CSV extract expected by
`scripts/derive_rail_shortest_path_evidence.py`. The command does not call live
APIs. It converts a reviewed station-to-station shortest-path result into a
`rail_service_evidence.csv` row with `source_status=cached_shortest_path_derived`
and `derived_fields=travel_time`.

The intended official source context for the pilot region is the Seoul Open
Data Plaza Seoul Metro shortest-path API:
<https://data.seoul.go.kr/dataList/OA-22724/A/1/datasetView.do>.
The same API is documented through data.go.kr as
`https://apis.data.go.kr/B553766/path/getShtrmPath`, with required
`serviceKey`, `dptreStnNm`, `arvlStnNm`, and `searchDt` parameters. The live
API requires a data.go.kr service key, so live fetching is optional and is not
part of default tests.

## Required Columns

| Column | Meaning |
| --- | --- |
| `route_id` | Stable route identifier within the cached extract. |
| `access_station_name` | Human-readable access station name from the source. |
| `access_station_code` | Official or source-specific access station code. |
| `egress_station_name` | Human-readable egress station name from the source. |
| `egress_station_code` | Official or source-specific egress station code. |
| `travel_time_min` | Source travel time in minutes. |
| `distance_km` | Source route distance in kilometers. |
| `transfer_count` | Number of transfers in the source route. |
| `route_type` | Source route type, for example `minimum_time`, `shortest_distance`, or `minimum_transfer`. |

The derivation selects the fastest row for the requested `route_type`, records
the cached input path and SHA256 digest, and validates station codes against
`data/parameters/rail_station_bindings.csv` by default. It does not derive
headway or capacity. Those must remain separate evidence fields or explicit
sensitivity-only assumptions.

## Command Template

```powershell
.\.venv\Scripts\python scripts\derive_rail_shortest_path_evidence.py `
  --input data\rail\pilot_rail_shortest_path_cache.csv `
  --output data\parameters\rail_service_evidence.csv `
  --evidence-id songpa_public_demo_rail_shortest_path_v1 `
  --region-id songpa_public_demo `
  --access-point S `
  --egress-point R `
  --source-name "Cached Seoul subway shortest-path extract" `
  --source-url-or-citation "https://data.seoul.go.kr/dataList/OA-22724/A/1/datasetView.do" `
  --extraction-date 2026-05-04 `
  --headway-min-proxy 10 `
  --capacity-pax-per-train 500 `
  --service-window "selected public-service planning window" `
  --route-type minimum_time `
  --station-bindings data\parameters\rail_station_bindings.csv
```

Do not use an invented shortest-path row for final-study claims. The cached
extract must come from an official or explicitly accepted source, and the
source URL, access date, station-code binding, route type, and transformation
steps must be documented.

## Optional Live Fetch

The repository includes an optional helper for creating the local cache from a
reviewed data.go.kr shortest-path API request:

```powershell
.\.venv\Scripts\python scripts\fetch_rail_shortest_path_cache.py `
  --departure-station-name 올림픽공원 `
  --arrival-station-name 잠실 `
  --search-dt "2026-05-04 09:00:00" `
  --access-station-name 올림픽공원 `
  --access-station-code 936 `
  --egress-station-name 잠실 `
  --egress-station-code 814 `
  --output data\rail\pilot_rail_shortest_path_cache.csv `
  --raw-output data\rail\pilot_rail_shortest_path_raw.json
```

Set `DATA_GO_KR_KEY` before running the command, or pass `--service-key`.
The command writes the local cache schema only. It does not update
`rail_service_evidence.csv`; run `scripts\derive_rail_shortest_path_evidence.py`
after the cached extract is reviewed. The fetcher records the official API
response as raw JSON when `--raw-output` is supplied so reviewers can inspect
the source payload before any manuscript claim is upgraded.
