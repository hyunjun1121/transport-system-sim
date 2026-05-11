# Third-Party Adaptation Records

> Current project status (2026-05-08): `final_study_ready=false`. Ready gates are `3/15` (`real_input_smoke`, `structured_disruptions`, `policy_alternatives`), blocked gates are `12/15`, and formal acceptance is `0/12` ready. This document is current-state or review support only; it does not create formal approval, calibrated real-world results, or operational routing guidance.


This file records public-repository influence for the real-world MVP. Runtime
code must not import from `cloned_repo/`, and no files inside `cloned_repo/`
should be edited as part of implementation.

## Summary

No third-party source files or functions were copied into `src/realworld/` for
the MVP documentation wave. The implementation uses public libraries through
normal package imports where already appropriate, and it reimplements the small
adapter behaviors locally around this project's simulator contract.

## Records

| Source repository | Source file or function | License | Local destination | Adaptation type | Reason | Tests |
| --- | --- | --- | --- | --- | --- | --- |
| `cloned_repo/osmnx` | API convention for `graph_from_bbox` and OSMnx-style graph attributes such as node `x`/`y`, edge `length`, `highway`, `maxspeed`, and `osmid` | MIT; OSM data attribution obligations still apply when live OSM data are used | `src/realworld/osm_network.py`, `src/realworld/attributes.py`, `src/realworld/zones.py` | reimplemented idea / interface adaptation | Keep OSMnx optional and avoid making live OSM access a unit-test dependency | `tests/test_realworld_osm_network.py`, `tests/test_realworld_attributes.py`, `tests/test_realworld_adapter.py` |
| `cloned_repo/networkx` | GraphML read/write and graph/path interfaces as public dependency behavior | BSD-3-Clause | `src/realworld/osm_network.py`, `src/realworld/adapter.py`, `src/realworld/validation.py` | interface adaptation | The simulator already uses NetworkX; local code adapts graph contracts rather than copying NetworkX internals | `tests/test_realworld_osm_network.py`, `tests/test_realworld_adapter.py`, `tests/test_realworld_validation.py`, `tests/test_realworld_end_to_end.py` |

## Policy For Future Adaptations

When future workers use material from public repositories:

- Check the source license before copying non-trivial code.
- Prefer local reimplementation of small ideas over direct copying.
- Keep any copied helper small, tested, and under `src/realworld/` or another
  project-owned runtime path.
- Record the exact source path, symbol, license, local destination, adaptation
  type, reason, and test coverage in this file.
- Do not import runtime modules from `cloned_repo/`.
