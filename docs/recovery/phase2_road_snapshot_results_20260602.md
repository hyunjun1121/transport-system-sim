# Phase 2 Road Snapshot Results - 2026-06-02

## Scope

This note records the Phase 2 progress made under `plan.md`: region-level road
snapshot artifacts for the real-world input pipeline.

The work is review-support only. It does not create source-provenance
acceptance, graph-scale acceptance, validation acceptance, final-audit
acceptance, or operational routing evidence.

## Files Added Or Updated

- Added `src/realworld/road_snapshot.py`.
- Added `scripts/write_road_snapshot.py`.
- Added `tests/test_realworld_road_snapshot.py`.
- Updated `src/realworld/__init__.py` to export road-snapshot helpers.
- Updated `src/realworld/osm_network.py` so GraphML save handles
  `node_default` and `edge_default` metadata from cached GraphML safely.
- Updated `tests/test_realworld_osm_network.py` with a GraphML default-metadata
  regression test.

## Implemented Behavior

- Writes timestamped or explicit road snapshot output directories.
- Writes:
  - `road.graphml`;
  - `road_nodes.csv`;
  - `road_edges.csv`;
  - `connector_audit.csv`;
  - `road_snapshot_manifest.json`.
- Computes SHA256 and byte counts for generated GraphML and CSV artifacts.
- Records non-acceptance claim boundaries:
  - `formal_acceptance_created=false`;
  - `can_mark_complete=false`.
- Refuses to overwrite a non-empty output directory unless `overwrite=True`.
- Audits connectors from assembly, destination, rail-access, and rail-egress
  points to routeable vehicle-road nodes, not pedestrian-only nodes.

## Commands Run

```powershell
.\.venv\Scripts\python tests\test_realworld_road_snapshot.py
.\.venv\Scripts\python tests\test_realworld_osm_network.py
.\.venv\Scripts\python tests\test_realworld_adapter.py
.\.venv\Scripts\python tests\test_realworld_validation.py
.\.venv\Scripts\python tests\test_realworld_end_to_end.py
.\.venv\Scripts\python tests\test_realworld_osm_graph_snapshot_review_packet.py
.\.venv\Scripts\python tests\test_config.py
```

All listed tests passed.

The new CLI was also smoke-tested against the cached pilot GraphML with:

```powershell
.\.venv\Scripts\python scripts\write_road_snapshot.py --region-id songpa_public_demo --region-path data\regions\pilot_region.yaml --source cached --source-graph data\cache\pilot_region_road.graphml --output-dir <temp-dir> --created-utc 2026-06-02T00:00:00+00:00
```

The smoke output contained:

- `road.graphml`, 12,097,745 bytes;
- `road_nodes.csv`, 599,282 bytes;
- `road_edges.csv`, 2,661,097 bytes;
- `connector_audit.csv`, 616 bytes;
- `road_snapshot_manifest.json`, 2,933 bytes.

The manifest reported:

- `node_count=13268`;
- `edge_count=28947`;
- `routeable_edge_count` recorded by the generated manifest;
- `connector_audit_row_count=4`;
- all connector rows classified as `ok_connector_distance`;
- `max_connector_distance_m=519.610398`;
- `max_connector_t0_min=1.558831`;
- `formal_acceptance_created=false`;
- `can_mark_complete=false`.

## Acceptance Hygiene Check

The following formal acceptance targets remained absent after this Phase 2
work:

- `data/manifests/provenance_acceptance.json`;
- `data/manifests/graph_scale_acceptance.json`;
- `data/manifests/validation_acceptance.json`;
- `data/manifests/final_audit_acceptance.json`.

A targeted search of the new Phase 2 files found no `accepted: true`,
`can_mark_complete: true`, or `formal_acceptance_created: true` strings.

## Remaining Phase 2 Work

- Add deeper geometry retention support if route geometry figures or polygon
  clipping become required.
- Add a pinned PBF workflow after the cached GraphML interface is stable.
- Add connector dominance checks against route travel time once route-level
  benchmark outputs are available.
- Decide whether generated road snapshot artifacts should be retained in a
  permanent run directory or kept as temp smoke evidence only.
