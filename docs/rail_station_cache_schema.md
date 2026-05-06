# Rail Station Cache Schema

> Current project status (2026-05-06): `final_study_ready=false`. Ready gates are `3/15` (`real_input_smoke`, `structured_disruptions`, `policy_alternatives`), blocked gates are `12/15`, and formal acceptance is `0/12` ready. This document is current-state or review support only; it does not create formal approval, calibrated real-world results, or operational routing guidance.


This schema defines the local CSV extract expected by
`scripts/derive_rail_station_bindings.py`. The command does not call live APIs.
It converts a reviewed official station source into
`data/parameters/rail_station_bindings.csv` format.

The current repository ships a reviewed station-code cache for
`songpa_public_demo` at:

```text
data/rail/pilot_station_binding_cache.csv
```

It is derived from Seoul Open Data Plaza station-name search responses for
Olympic Park and Jamsil. The generated binding rows close the station-identifier
gate only. They do not validate rail headway, rail travel time, train capacity,
route choice, or emergency rail availability.

## Required Columns

| Column | Meaning |
| --- | --- |
| `point_id` | Simulator rail point, for example `S` or `R`. |
| `station_name` | Station name from the reviewed source extract. |
| `station_id` | Official or source-specific station identifier. Use `pending` only in non-derived context rows, not in this cache. |
| `station_code` | Official or source-specific station code. Use `pending` only in non-derived context rows, not in this cache. |
| `line` | Source line or route label used to disambiguate transfer stations. |

At least one of `station_id` or `station_code` must be a non-placeholder
identifier for each row. Interchange stations may appear as multiple
line-specific rows for the same simulator point. Exact duplicate rows for the
same point, station ID, station code, and line are rejected.

## Command Template

```powershell
.\.venv\Scripts\python scripts\derive_rail_station_bindings.py `
  --input data\rail\pilot_station_binding_cache.csv `
  --output data\parameters\rail_station_bindings.csv `
  --binding-id-prefix songpa_public_demo_station_binding_v1 `
  --region-id songpa_public_demo `
  --source-name "Seoul Open Data Plaza SearchInfoBySubwayNameService cached extract" `
  --source-url-or-citation "https://data.seoul.go.kr/dataList/OA-121/S/1/datasetView.do" `
  --source-accessed-date 2026-05-04 `
  --required-points S,R
```

Do not run this command against invented station codes. The input file must be
a cached extract from an official or explicitly accepted source, and the source
URL, access date, and any transformation steps must be documented before
final-study rail claims are upgraded.
