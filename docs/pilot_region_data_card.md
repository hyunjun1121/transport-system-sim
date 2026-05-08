# Pilot Region Data Card

> Current project status (2026-05-08): `final_study_ready=false`. Ready gates are `3/15` (`real_input_smoke`, `structured_disruptions`, `policy_alternatives`), blocked gates are `12/15`, and formal acceptance is `0/12` ready. This document is current-state or review support only; it does not create formal approval, calibrated real-world results, or operational routing guidance.


## Region

The pilot region is `songpa_public_demo`, a non-sensitive public demonstration
area in Songpa-gu, Seoul. It is used to prove that the real-world input pathway
can load a region spec, load a cached road graph, create simulator connectors,
and run both bus-only and rail-bus multimodal smoke scenarios.

This pilot is a quasi-real demonstration case. It is not a calibrated emergency
or military operation plan.

## Coordinates

| Simulator ID | Meaning | Coordinate Class | Sensitivity Handling |
| --- | --- | --- | --- |
| `A` | public assembly demonstration zone near Olympic Park | public | public civic area, not an operational assembly order |
| `D` | public destination demonstration zone near Jamsil | synthetic | synthetic public-zone centroid, not a protected destination |
| `S` | rail access demonstration point near Olympic Park Station | public | public station area |
| `R` | rail egress demonstration point near Jamsil Station | public | public station area |

The coordinates are stored in `data/regions/pilot_region.yaml`. The destination
is intentionally synthetic to avoid presenting a sensitive exact destination.

## Road Cache

The default cache path is:

```text
data/cache/pilot_region_road.graphml
```

The current cache manifest records a live Overpass/OSM-derived GraphML snapshot
for this public demo region. It is intended for offline smoke tests, scaffold
sample experiments, and reproducibility. It should still be reviewed for source
quality, connector plausibility, route realism, and attribution before any
stronger real-world result claim.

## Rail Assumptions

The current rail values in `pilot_region.yaml` are documented assumptions:

- rail travel time: 20 minutes
- rail headway: 10 minutes
- train capacity: 500 passengers

These values support smoke testing only. Before publication-style claims, they
must be replaced by GTFS, public timetable evidence, agency documentation, or
clearly labeled sensitivity-only assumptions.

## Privacy And Security

This pilot uses only public or synthetic points. It does not disclose private
movement data, exact sensitive destinations, protected facility locations, or
operational routing instructions.

Acceptable claims:

- The pilot demonstrates an offline real-world-style input pathway.
- The graph cache can be converted into a simulator-ready graph.
- The scenario runner can execute both bus-only and multimodal smoke cases.

Avoid:

- claiming the cache is a calibrated OSM/Songpa transport model
- claiming the rail assumptions represent emergency operations
- using the pilot as an operational route plan

## Reuse For Other Regions

To add another region, create a new region spec, cache, data card, and parameter
rows with a different `region_id`. Shared code should not require changes.
