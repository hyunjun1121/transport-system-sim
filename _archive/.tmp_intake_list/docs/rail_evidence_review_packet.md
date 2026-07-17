# Rail Evidence Review Packet

> Current project status (2026-05-08): `final_study_ready=false`. Ready gates are `3/15` (`real_input_smoke`, `structured_disruptions`, `policy_alternatives`), blocked gates are `12/15`, and formal acceptance is `0/12` ready. This document is current-state or review support only; it does not create formal approval, calibrated real-world results, or operational routing guidance.


This note documents `data/parameters/rail_evidence_review_packet.csv` and
`data/parameters/rail_evidence_review_manifest.json`.

The packet is a review aid only. It does not create calibrated rail-service
timing evidence, GTFS validation, emergency rail availability evidence, or
operational route guidance.

## Scope

The packet consolidates:

- official station-code binding status for simulator rail points `S` and `R`,
- current rail headway, travel-time, and capacity evidence status,
- rail service-window and availability assumptions,
- available local derivation paths for timetable, GTFS, and shortest-path
  evidence.

The current generated packet has 10 rows. The two station-binding rows are
ready as station identifiers only. The headway and travel-time rows remain weak
because no reviewed cached timetable, GTFS, or shortest-path source artifact is
committed. The rail-capacity row now surfaces the cached Metro9 capacity
extract and raw operator-page snapshot as review input, but capacity is still
retained as an explicit sensitivity-only value, not a source-backed emergency
capacity claim.

## Regeneration

```powershell
.\.venv\Scripts\python scripts\write_rail_evidence_review_packet.py
```

Expected outputs:

- `data/parameters/rail_evidence_review_packet.csv`
- `data/parameters/rail_evidence_review_manifest.json`

The manifest should keep `publication_ready: false` until cached rail timing
evidence derives both headway and travel time and records source artifact path
plus SHA256.

## Review Use

Use this packet to decide which rail evidence artifact to prepare next:

- a reviewed station-event timetable cache,
- a reviewed static GTFS feed,
- a reviewed station-to-station shortest-path cache,
- a separate source-backed or sensitivity-only capacity treatment,
- rail delay, unavailability, and station-access disruption scenarios.

Do not use the packet as evidence that the current rail leg is calibrated or
available for emergency operations.
