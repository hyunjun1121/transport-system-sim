# Rail Timing Source-Request Packet

> Current project status (2026-05-08): `final_study_ready=false`. Ready gates are `3/15` (`real_input_smoke`, `structured_disruptions`, `policy_alternatives`), blocked gates are `12/15`, and formal acceptance is `0/12` ready. This document is current-state or review support only; it does not create formal approval, calibrated real-world results, or operational routing guidance.


This note documents `data/rail/rail_timing_source_request_packet.csv` and
`data/rail/rail_timing_source_request_manifest.json`.

The packet does not contain rail timing observations. It names the reviewed
source inputs required before rail headway and travel-time claims can be
strengthened.

## Scope

The packet records five request rows:

- a data.go.kr train-schedule request for headway evidence,
- a data.go.kr shortest-path request for station-to-station travel-time
  evidence,
- a reviewed static-GTFS request that could derive both headway and travel
  time,
- a capacity-treatment request,
- a rail availability and delay-scenario request.

The current live API paths require `DATA_GO_KR_KEY` or an explicit
`--service-key`. The static-GTFS path requires a reviewed GTFS zip or
directory plus reviewed access stop, egress stop, route, and service-window
choices.

## Regeneration

```powershell
.\.venv\Scripts\python scripts\write_rail_timing_source_request_packet.py
```

Expected outputs:

- `data/rail/rail_timing_source_request_packet.csv`
- `data/rail/rail_timing_source_request_manifest.json`

The manifest should keep `publication_ready: false` because this packet is a
source-request worksheet, not evidence.

## Review Use

Use this packet before running live rail fetches or committing GTFS data. Each
row states:

- which evidence field the source can support,
- which external key, file, or reviewed decision is required,
- which local cache path should be produced,
- which derivation command should convert the cache into
  `rail_service_evidence.csv`,
- why the row does or does not close the rail timing gate by itself.

Do not use the packet as proof that the current rail headway, travel time,
capacity, or availability values are calibrated.
