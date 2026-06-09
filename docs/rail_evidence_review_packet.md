# Rail Evidence Review Packet

> Current project status (2026-05-08): the study-closeout flag is false. Three scaffold checks are open (`real_input_smoke`, `structured_disruptions`, `policy_alternatives`), twelve closeout gates remain blocked, and formal acceptance is `0/12`. This document is current-state or review support only; it does not create formal approval, calibrated real-world results, or route-use guidance.


This note documents `data/parameters/rail_evidence_review_packet.csv` and
`data/parameters/rail_evidence_review_manifest.json`.

The packet is a review aid only. It does not create rail-service timing
evidence, GTFS validation, emergency rail availability evidence, or route-use
guidance.

## Scope

The packet consolidates:

- official station-code binding status for simulator rail points `S` and `R`,
- current rail headway, travel-time, and capacity evidence status,
- rail service-window and availability assumptions,
- available local derivation paths for timetable, GTFS, and shortest-path
  evidence,
- retained static timetable cache and segment-pair diagnostic artifacts as
  review-only non-evidence rows.

The current generated packet has 12 rows. The two station-binding rows are
bound as station identifiers only. The headway and travel-time rows remain weak
because no reviewed cached timetable, GTFS, or shortest-path source artifact is
committed. The rail-capacity row now surfaces the cached Metro9 capacity
extract and raw operator-page snapshot as review input, but capacity is still
retained as an explicit sensitivity-only value, not a source-backed emergency
capacity claim. The static timetable cache and segment-pair diagnostic rows
are visible for reviewer triage only; they do not derive
`rail_service_evidence.csv`, validate observed transfer movement, or close rail
evidence gates.

## Regeneration

```powershell
.\.venv\Scripts\python scripts\write_rail_evidence_review_packet.py
```

Expected outputs:

- `data/parameters/rail_evidence_review_packet.csv`
- `data/parameters/rail_evidence_review_manifest.json`

The manifest should keep its publication gate boolean false until cached rail
timing evidence derives both headway and travel time and records source
artifact path plus SHA256.

## Review Use

Use this packet to decide which rail evidence artifact to prepare next:

- a reviewed station-event timetable cache,
- a reviewed static GTFS feed,
- a reviewed station-to-station shortest-path cache,
- a reviewer decision on whether the retained static timetable cache can be
  used only for headway-review preparation,
- a separate transfer or station-circulation evidence source if the
  segment-pair diagnostic is to inform release-scope claims,
- a separate source-backed or sensitivity-only capacity treatment,
- rail delay, unavailability, and station-access disruption scenarios.

Do not use the packet as evidence that the current rail leg has reviewed timing
support or emergency-service availability.
