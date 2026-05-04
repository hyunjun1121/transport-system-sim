# Rail GTFS Cache Schema

This schema documents the cached static GTFS input supported by
`scripts/derive_rail_gtfs_evidence.py`.

The command does not call live APIs. It reads a reviewed GTFS zip or directory,
selects trips between a configured access stop and egress stop, and writes one
`rail_service_evidence.csv` row with `source_status=cached_gtfs_derived`.

## Required GTFS Files

The minimum supported static GTFS files are:

| File | Required columns | Use |
| --- | --- | --- |
| `stops.txt` | `stop_id`, `stop_name` | Resolves access and egress stop names. |
| `trips.txt` | `trip_id`, `route_id`, `service_id`, optional `direction_id` | Filters trips by route, service, and direction. |
| `stop_times.txt` | `trip_id`, `arrival_time`, `departure_time`, `stop_id`, `stop_sequence` | Computes access-station headways and stop-to-stop travel time. |

Times may use standard GTFS service-hour notation, including hours above 24.

## Derived Fields

The derivation writes:

- median access-stop headway from consecutive selected trip departures;
- median access-to-egress scheduled travel time from selected trip stop times;
- configured train capacity from the command line;
- `source_status=cached_gtfs_derived`;
- `derived_fields=headway;travel_time`;
- `source_artifact_path` and `source_artifact_sha256`.

Capacity is not inferred from GTFS. It remains a supplied capacity value and
should be source-backed or explicitly retained as sensitivity-only before final
claims.

## Command Template

Prefer a reviewed GTFS zip for reproducibility:

```powershell
.\.venv\Scripts\python scripts\derive_rail_gtfs_evidence.py `
  --input data\rail\pilot_gtfs.zip `
  --output data\parameters\rail_service_evidence.csv `
  --evidence-id songpa_public_demo_rail_gtfs_v1 `
  --region-id songpa_public_demo `
  --access-point S `
  --egress-point R `
  --access-stop-id ACCESS_STOP_ID `
  --egress-stop-id EGRESS_STOP_ID `
  --source-name "Reviewed static GTFS feed" `
  --source-url-or-citation "GTFS source URL or citation" `
  --extraction-date 2026-05-04 `
  --capacity-pax-per-train 500 `
  --service-window "weekday selected service window" `
  --route-id ROUTE_ID `
  --service-id SERVICE_ID `
  --direction-id 0
```

Directory inputs are accepted for local review, but a zip file should be used
for final reproducibility because the rail-evidence audit verifies a single
artifact path and SHA256 digest.

## Claim Boundary

A GTFS-derived row supports scheduled-service timing evidence only. It does not
prove emergency rail availability, station crowd handling, special train
operations, disruption response, or train capacity. The row can close the rail
timing evidence blocker only when the GTFS artifact is reviewed, the source
path resolves, the SHA256 matches, and the final claim boundary keeps rail
operations as a planning scenario rather than an operational guarantee.

Before final claims, also verify:

- station identifiers and stop choices are reviewed against the pilot rail
  access and egress points;
- rail capacity is source-backed or deliberately retained as sensitivity-only;
- rail delay or unavailability scenarios are included where relevant;
- `scripts/audit_rail_evidence.py` reports timing evidence readiness.
