# Road Evidence Source-Request Packet

> Current project status (2026-05-06): `final_study_ready=false`. Ready gates are `3/15` (`real_input_smoke`, `structured_disruptions`, `policy_alternatives`), blocked gates are `12/15`, and formal acceptance is `0/12` ready. This document is current-state or review support only; it does not create formal approval, calibrated real-world results, or operational routing guidance.


This note documents `data/road/road_evidence_source_request_packet.csv` and
`data/road/road_evidence_source_request_manifest.json`.

The packet does not contain reviewed road observations. It names the source
inputs required before road speed, capacity, background-traffic, disruption,
and override-application claims can be strengthened.

## Scope

The packet records five request rows:

- a speed-limit or benchmark request for road-class free-flow speed evidence,
- a lane, traffic-count, or capacity-reference request,
- a route-benchmark and background-traffic treatment request,
- a hazard, incident, exposure, or reviewed scenario-rule request for
  disruption probabilities and blockage/capacity-reduction behavior,
- a reviewed override-table and manifest-application request.

The final row names the closure path, but the packet itself does not close the
road-evidence or road-application gate. Closure still requires a reviewed
`data/parameters/road_class_overrides.csv` table, a rerun that records the
table path and SHA256 in the result manifest, and explicit acceptance records.

## Regeneration

```powershell
.\.venv\Scripts\python scripts\write_road_evidence_source_request_packet.py
```

Expected outputs:

- `data/road/road_evidence_source_request_packet.csv`
- `data/road/road_evidence_source_request_manifest.json`

The manifest should keep `publication_ready: false` because this packet is a
source-request worksheet, not evidence.

## Review Use

Use this packet before creating `data/parameters/road_class_overrides.csv`.
Each row states:

- which evidence field the source can support,
- which external source, reviewed file, or reviewer decision is required,
- which local cache or diagnostic artifact already exists,
- which command or review step should be run next,
- whether the resulting source package can help close the evidence or
  application gate after review.

Do not use the packet as proof that current road speed, capacity, background
traffic, disruption, or route-choice assumptions are calibrated.
