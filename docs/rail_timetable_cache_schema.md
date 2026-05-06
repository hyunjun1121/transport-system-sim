# Rail Timetable Cache Schema

> Current project status (2026-05-06): `final_study_ready=false`. Ready gates are `3/15` (`real_input_smoke`, `structured_disruptions`, `policy_alternatives`), blocked gates are `12/15`, and formal acceptance is `0/12` ready. This document is current-state or review support only; it does not create formal approval, calibrated real-world results, or operational routing guidance.


This schema defines the local CSV extract expected by
`scripts/derive_rail_service_evidence.py`. The command does not call live APIs.
It converts a reviewed timetable extract into `rail_service_evidence.csv`
format so rail headway and travel time can be audited as cached evidence.
The derivation command records the cached input path and SHA256 digest in the
evidence row notes and optional evidence columns, preserving reproducibility
without requiring a live API in default tests. The rail evidence audit counts a
derived row as ready only when the artifact path resolves and the SHA256
matches.

## Required Columns

| Column | Meaning |
| --- | --- |
| `trip_id` | Stable train or trip identifier within the cached extract. |
| `station_role` | `access` for the rail boarding station or `egress` for the alighting station. |
| `station_name` | Human-readable station name from the source extract. |
| `station_code` | Official or source-specific station code. |
| `event_time` | `HH:MM` or `HH:MM:SS`; GTFS-style hours above 24 are allowed. |
| `event_type` | `departure` for access events or `arrival` for egress events. |
| `direction` | Direction label from the source extract, for example `eastbound`. |
| `service_day` | Service-day label, for example `weekday`, `saturday`, or `holiday`. |

The derivation requires at least two access departures and at least one matched
`trip_id` with an access departure and egress arrival. By default, the command
also loads `data/parameters/rail_station_bindings.csv` and checks that access
and egress station codes in the cached extract match official station bindings
for the configured `S` and `R` rail points. It writes:

- median access-station headway;
- median matched access-to-egress travel time;
- configured train capacity from the command line;
- `source_status=cached_timetable_derived`;
- `derived_fields=headway;travel_time`;
- a conservative claim scope: cached timetable-derived evidence, not an
  operational forecast.
- `source_artifact_path` and `source_artifact_sha256` in the evidence notes.

Rail capacity is intentionally not treated as timetable-derived by this path.
The command carries a reviewed or accepted capacity value into the evidence row
and marks it as sensitivity-only unless a separate source-backed capacity record
is provided.

## Headway-Only Derivation

If the reviewed timetable source reliably supports access-station departures
but does not provide a matched access-to-egress travel time, derive headway only:

```powershell
.\.venv\Scripts\python scripts\derive_rail_headway_evidence.py `
  --input data\rail\pilot_rail_timetable_cache.csv `
  --output data\parameters\rail_service_evidence.csv `
  --evidence-id songpa_public_demo_rail_headway_v1 `
  --region-id songpa_public_demo `
  --access-point S `
  --egress-point R `
  --egress-station-name "Jamsil" `
  --source-name "Cached Seoul subway train schedule extract" `
  --source-url-or-citation "https://www.data.go.kr/en/data/15143847/openapi.do" `
  --extraction-date 2026-05-04 `
  --travel-time-min-proxy 20 `
  --capacity-pax-per-train 500 `
  --service-window "weekday selected service window" `
  --direction "?ÅÌñâ" `
  --service-day "?âÏùº" `
  --station-bindings data\parameters\rail_station_bindings.csv
```

The resulting row has `derived_fields=headway`. The positive
`travel_time_min_proxy` is carried only because the repository evidence schema
stores one rail-service row shape. It cannot satisfy the travel-time evidence
gate. Pair this with a reviewed shortest-path, GTFS, or matched timetable row
before upgrading rail timing claims.

## Optional Live Fetch

The repository includes an optional helper for creating the local timetable
cache from a reviewed data.go.kr train-schedule API request:

```powershell
.\.venv\Scripts\python scripts\fetch_rail_timetable_cache.py `
  --line-name "9?∏ÏÑ†" `
  --upbdnb-se "?ÅÌñâ" `
  --wknd-se "?âÏùº" `
  --station-name "?¨Î¶º?ΩÍ≥µ?? `
  --station-code 936 `
  --access-station-name "?¨Î¶º?ΩÍ≥µ?? `
  --access-station-code 936 `
  --output data\rail\pilot_rail_timetable_cache.csv `
  --raw-output data\rail\pilot_rail_timetable_raw.json
```

Set `DATA_GO_KR_KEY` before running the command, or pass `--service-key`. The
official data.go.kr endpoint is documented as
`http://apis.data.go.kr/B553766/schedule/getTrainSch`, with required
`serviceKey`, `tmprTmtblYn`, `upbdnbSe`, `wkndSe`, and `lineNm` parameters.
The command writes the local cache schema only. It does not update
`rail_service_evidence.csv`; run one of the derivation commands after the
cached extract is reviewed.

## Command Template

```powershell
.\.venv\Scripts\python scripts\derive_rail_service_evidence.py `
  --input data\rail\pilot_rail_timetable_cache.csv `
  --output data\parameters\rail_service_evidence.csv `
  --evidence-id songpa_public_demo_rail_timetable_v1 `
  --region-id songpa_public_demo `
  --access-point S `
  --egress-point R `
  --source-name "Cached Seoul subway timetable extract" `
  --source-url-or-citation "https://data.seoul.go.kr/dataList/32/literacyView.do; https://www.data.go.kr/en/data/15143847/openapi.do" `
  --extraction-date 2026-05-04 `
  --capacity-pax-per-train 500 `
  --service-window "weekday selected service window" `
  --direction eastbound `
  --service-day weekday `
  --station-bindings data\parameters\rail_station_bindings.csv
```

Do not run this command against an invented timetable. The input file must be a
cached extract from an official or explicitly accepted source, and the source
URL, extraction date, station-code binding, and any transformation steps must
be documented before final-study claims are upgraded.

Before using a derived row for final-study claims, also run:

```powershell
.\.venv\Scripts\python scripts\audit_rail_station_bindings.py
```

The station-binding audit now reports `binding_ready: true` for the pilot
station identifiers. That does not make rail timing claims publication-ready;
headway and travel time still need cached timetable, GTFS, shortest-path, or
equivalent service evidence. The rail-service audit now tracks derived fields
separately so a future shortest-path-only row cannot accidentally certify
headway evidence, and a future timetable-only headway row can be combined with
a separate cached shortest-path travel-time row.

Use `docs/rail_station_cache_schema.md` and
`scripts/derive_rail_station_bindings.py` to create official station bindings
from a reviewed station source before deriving final-study rail timing claims.
