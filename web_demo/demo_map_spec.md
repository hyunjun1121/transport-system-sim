# Web Demo Map Specification

Last updated: 2026-05-13

## Fixed Scenario

The web demo uses exactly one scenario:

> Seoul/Suseo-area assembly and rail access to the Pyeongtaek-Jije transfer area and a generalized Pyeongtaek support zone.

This is a public-data, non-operational, non-final decision-support sample. It must not be described as an actual dispatch plan, operational route order, real travel-time forecast, or accepted field evidence.

## Map Markers

| Node | UI label | Role | Example coordinate | Evidence status | Display rule |
|---|---|---|---|---|---|
| A | Suseo Area Assembly Zone | Assembly | 37.5030, 127.0870 | Generalized example | Area-level marker only |
| S | Suseo Rail Access Hub | Rail access | 37.4875, 127.1010 | Public station-area anchor | Do not describe as exact pickup point |
| R | Pyeongtaek-Jije Transfer Area | Rail transfer | 37.0188, 127.0707 | Public station-area anchor | Do not describe as exact drop-off point |
| D | Pyeongtaek Support Zone | Destination zone | 36.9920, 127.1120 | Generalized support-area marker | Do not name sensitive facilities |
| D1 | Road Contingency Waypoint A | Road waypoint | 37.3050, 127.1420 | Abstract waypoint | Show corridor redundancy only |
| D2 | Road Contingency Waypoint B | Road waypoint | 37.2050, 126.9850 | Abstract waypoint | Show disruption sensitivity only |

## Route Layers

- Bus-only layer: red dashed road corridor using the configured `bus_single_corridor` links.
- Rail-bus layer: blue dashed road access/egress links plus teal rail segment between Suseo and Pyeongtaek-Jije.
- Moving teal dots: abstract flow markers for the rail-bus sample, not real-time vehicle tracking.

## Required On-Screen Boundaries

The map must show or imply all of the following:

- Public-data, non-operational sample.
- Generalized area labels.
- Not pickup orders, dispatch guidance, or accepted field evidence.
- Bus-only and rail-bus options are comparative simulation samples.

## Verification Checklist

- [ ] All visible labels use the fixed scenario.
- [ ] No sensitive facility name appears.
- [ ] No turn-by-turn route instruction appears.
- [ ] Map renders markers and route lines at desktop width.
- [ ] Map renders without label overlap severe enough to hide the scenario at mobile width.
- [ ] Screenshot captions use "sample", "non-operational", and "decision-support" language.
