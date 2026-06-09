# Phase 3 Road Override Metadata Traceability

## Scope

This sprint adds traceability for reviewer-supplied road-class override metadata.
It does not create `data/parameters/road_class_overrides.csv`, does not accept
road calibration evidence, does not close cached OSM input, validation,
publication, formal acceptance, or final-study gates, and does not change the
project-wide `final_study_ready=false` boundary.

## Code Changes

- `src/realworld/road_overrides.py`
  - added `build_road_class_override_metadata()` so loaded override rows can
    preserve source class, source name, citation, notes, and numeric values
    separately from mapper defaults.
- `src/realworld/adapter.py`
  - added optional `road_class_override_metadata` propagation.
  - edge metadata is attached only when the mapped edge actually used an
    override-backed fallback field: `speed_kph`, `capacity`, or `base_p_fail`.
- `src/realworld/pilot_experiments.py`
  - when a road override table path is explicitly supplied, the pilot input
    loader now passes both override defaults and source metadata into graph
    adaptation.
- `src/realworld/route_road_evidence_exposure.py`
  - route-level review rows surface edge-level override `source_class` when it
    is present, while keeping `weak_for_final_claim` governed by the existing
    review packet.
- `src/realworld/__init__.py`
  - exported the new metadata helper.

## Tests And Checks

| Command | Result | Boundary |
| --- | --- | --- |
| `.\.venv\Scripts\python tests\test_realworld_road_overrides.py` | passed | Loader and metadata helper only. |
| `.\.venv\Scripts\python tests\test_realworld_adapter.py` | passed | Graph edge metadata propagation only. |
| `.\.venv\Scripts\python tests\test_realworld_route_road_evidence_exposure.py` | passed | Current shipped exposure remains unchanged unless edge override metadata exists. |
| `.\.venv\Scripts\python tests\test_realworld_pilot_experiments.py` | passed | Pilot override path remains explicit and manifest-bounded. |
| `.\.venv\Scripts\python -m py_compile ...` | passed | Syntax check for touched modules and tests. |
| `.\.venv\Scripts\python scripts\audit_claim_language.py --fail-on-blockers` | passed with 0 blocking findings | Lexical guard only; not formal approval. |
| `.\.venv\Scripts\python tests\test_realworld_plan_audit.py` | passed after refreshing dirty-worktree classification | Plan artifact boundary remains fail-closed. |
| `git diff --check -- <touched paths>` | passed with line-ending warnings only | Whitespace check only. |

## Residual Blockers

- The reviewed override target `data/parameters/road_class_overrides.csv`
  remains absent.
- Route-level exposure remains review support only.
- Human/source-backed road evidence and formal decision records are still
  required before road evidence or final-study claims can close.
