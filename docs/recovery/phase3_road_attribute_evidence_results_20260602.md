# Phase 3 Road Attribute Evidence Results - 2026-06-02

## Scope

This phase adds edge-level road-attribute evidence for the real-world or
quasi-real simulation pipeline. The work is review support only. It does not
create reviewed road overrides, formal acceptance artifacts, calibrated traffic
assignment evidence, or operational routing evidence.

## Files Added Or Updated

Added:

- `src/realworld/road_attribute_evidence.py`
- `scripts/write_road_attribute_evidence.py`
- `tests/test_realworld_road_attribute_evidence.py`
- `docs/road_attribute_evidence.md`
- `data/parameters/road_attribute_evidence_table.csv`
- `data/parameters/road_attribute_evidence_manifest.json`

Updated:

- `src/realworld/attributes.py`
- `src/realworld/__init__.py`
- `src/realworld/final_study_readiness.py`
- `src/realworld/README.md`
- `plan.md`
- `tests/test_realworld_final_study_readiness.py`

## Implementation Notes

- Edge evidence rows now use a unique `edge_id` composed from `(u, v, key)` plus
  the source edge identifier where present.
- `realworld_edge_id` is preserved separately for OSM/provenance joins.
- OSM lane tags produce `lane_based_capacity_candidate_veh_per_hr`; they do not
  upgrade the currently used mapper capacity proxy.
- Mapper capacity fallback and base-disruption fallback are explicitly recorded
  in `attribute_assumptions`.
- Explicit numeric `capacity` and `base_p_fail` values are not treated as
  `source-backed` unless source markers are present.
- Optional benchmark travel times require benchmark source and snapshot
  metadata before `routing-engine benchmarked` is emitted.
- Final-study readiness now records the edge-level evidence table and manifest
  under the cached OSM input gate as traceability details only. This does not
  mark the gate ready and does not create any formal acceptance artifact.

## Generated Evidence Summary

Command:

```powershell
.\.venv\Scripts\python scripts\write_road_attribute_evidence.py
```

Manifest summary:

- `row_count`: 28,947
- `routeable_edge_count`: 9,140
- `weak_for_final_claim_count`: 28,947
- `speed_evidence_class_counts`: `OSM-derived=374`, `expert proxy=28,573`
- `capacity_evidence_class_counts`: `expert proxy=28,947`
- `base_disruption_evidence_class_counts`: `sensitivity-only=28,947`
- `publication_ready`: `false`
- `formal_acceptance_created`: `false`
- `can_mark_complete`: `false`

Output file sizes observed:

- `data/parameters/road_attribute_evidence_table.csv`: 13,564,232 bytes
- `data/parameters/road_attribute_evidence_manifest.json`: 1,852 bytes

## Tests And Checks Run

Passed:

```powershell
.\.venv\Scripts\python -m py_compile src\realworld\attributes.py src\realworld\road_attribute_evidence.py scripts\write_road_attribute_evidence.py tests\test_realworld_road_attribute_evidence.py
.\.venv\Scripts\python tests\test_realworld_attributes.py
.\.venv\Scripts\python tests\test_realworld_road_attribute_evidence.py
.\.venv\Scripts\python tests\test_realworld_road_capacity_evidence.py
.\.venv\Scripts\python tests\test_realworld_road_speed_evidence.py
.\.venv\Scripts\python tests\test_realworld_road_evidence.py
.\.venv\Scripts\python tests\test_traffic.py
.\.venv\Scripts\python tests\test_config.py
.\.venv\Scripts\python tests\test_scenario.py
.\.venv\Scripts\python tests\test_realworld_road_snapshot.py
.\.venv\Scripts\python tests\test_realworld_adapter.py
.\.venv\Scripts\python tests\test_realworld_validation.py
.\.venv\Scripts\python tests\test_realworld_end_to_end.py
.\.venv\Scripts\python tests\test_realworld_osm_network.py
.\.venv\Scripts\python main.py --test
```

Additional final-readiness integration checks passed:

```powershell
.\.venv\Scripts\python -m py_compile src\realworld\final_study_readiness.py tests\test_realworld_final_study_readiness.py
.\.venv\Scripts\python tests\test_realworld_final_study_readiness.py
```

CLI smoke passed with explicit temporary output paths:

```powershell
.\.venv\Scripts\python scripts\write_road_attribute_evidence.py --output <temp>\road_attribute.csv --manifest <temp>\road_attribute_manifest.json
```

Observed temporary output sizes:

- `road_attribute.csv`: 13,564,232 bytes
- `road_attribute_manifest.json`: 1,950 bytes

Formal hygiene checks:

```powershell
.\.venv\Scripts\python scripts\audit_formal_acceptance_artifacts.py
.\.venv\Scripts\python scripts\audit_final_study_readiness.py
```

Observed formal guard result:

- `template_or_placeholder_count`: 0
- `formal_acceptance_ready`: `false`
- `missing_count`: 12

Observed final-study readiness result:

- `final_study_ready`: `false`
- `verdict`: `final_real_world_study_blocked`
- blocked gates remain unchanged and expected.
- `cached_osm_input` details include the road-attribute evidence table and
  manifest, with `publication_ready=false`,
  `formal_acceptance_created=false`, and `can_mark_complete=false`.

Formal target files checked absent:

- `data/manifests/provenance_acceptance.json`
- `data/manifests/graph_scale_acceptance.json`
- `data/manifests/validation_acceptance.json`
- `data/manifests/final_audit_acceptance.json`
- `data/parameters/road_class_overrides.csv`

## Remaining Risks

- Current cached graph has sparse OSM maxspeed evidence and no parseable lane
  evidence in the generated edge table.
- All generated road-attribute rows remain `weak_for_final_claim=true`.
- Capacity values are still mapper proxies until reviewed road-class or
  edge-level overrides are supplied.
- Base disruption probabilities are sensitivity-only until reviewed hazard,
  incident, scenario, or expert evidence is supplied.
- The table is not integrated as a final-study acceptance gate; it is Phase 3
  review support for future road evidence decisions.
