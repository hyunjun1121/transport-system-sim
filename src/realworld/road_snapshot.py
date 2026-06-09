"""Road-network snapshot artifacts for the real-world input pipeline.

The snapshot writer is intentionally conservative: it writes review-support
artifacts for cached or live-extracted OSM-like graphs, but it does not create
formal acceptance records or claim calibrated real-world routing.
"""

from __future__ import annotations

import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Iterable, Mapping

import networkx as nx

from .attributes import is_routeable_vehicle_highway
from .osm_network import normalize_osm_graph, save_graphml
from .regions import load_region_spec
from .types import BoundarySpec, RegionSpec
from .zones import (
    DEFAULT_CONNECTOR_CAPACITY,
    DEFAULT_CONNECTOR_SPEED_KPH,
    MIN_CONNECTOR_T0_MIN,
    connector_edge_attributes,
    snap_region_points,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ROAD_SNAPSHOT_ROOT = PROJECT_ROOT / "data" / "cache" / "road_snapshots"
ROAD_SNAPSHOT_SCOPE = (
    "Road-network snapshot artifacts are review-support inputs only; they do "
    "not certify OSM/Overpass license compliance, road calibration, graph-scale "
    "acceptance, validation acceptance, or operational routing."
)
ROAD_SNAPSHOT_OUTPUTS = {
    "graphml": "road.graphml",
    "nodes_csv": "road_nodes.csv",
    "edges_csv": "road_edges.csv",
    "connector_audit_csv": "connector_audit.csv",
    "manifest": "road_snapshot_manifest.json",
}


def write_road_snapshot_artifacts(
    *,
    region: Mapping[str, Any] | RegionSpec,
    graph: nx.Graph,
    output_dir: str | Path,
    region_path: str | Path | None = None,
    source_graph_path: str | Path | None = None,
    source_type: str = "cached_graphml",
    overwrite: bool = False,
    created_utc: str | None = None,
    attribution: str = "OpenStreetMap contributors; respect OSM attribution requirements.",
    claim_boundary: str = ROAD_SNAPSHOT_SCOPE,
) -> dict[str, Any]:
    """Write GraphML, node/edge tables, connector audit, and manifest.

    Parameters are explicit so tests and scripts can use the same non-live
    artifact path. Existing output directories are not overwritten unless
    ``overwrite`` is true.
    """

    region_spec = load_region_spec(region)
    output = Path(output_dir)
    if output.exists() and any(output.iterdir()) and not overwrite:
        raise FileExistsError(
            f"Refusing to overwrite non-empty road snapshot directory: {output}"
        )
    output.mkdir(parents=True, exist_ok=True)

    normalized = normalize_osm_graph(graph)
    graph_path = output / ROAD_SNAPSHOT_OUTPUTS["graphml"]
    nodes_path = output / ROAD_SNAPSHOT_OUTPUTS["nodes_csv"]
    edges_path = output / ROAD_SNAPSHOT_OUTPUTS["edges_csv"]
    connectors_path = output / ROAD_SNAPSHOT_OUTPUTS["connector_audit_csv"]
    manifest_path = output / ROAD_SNAPSHOT_OUTPUTS["manifest"]

    save_graphml(normalized, graph_path)
    node_rows = road_node_rows(normalized)
    edge_rows = road_edge_rows(normalized)
    connector_rows = connector_audit_rows(normalized, region_spec)

    _write_csv(nodes_path, node_rows)
    _write_csv(edges_path, edge_rows)
    _write_csv(connectors_path, connector_rows)

    manifest = build_road_snapshot_manifest(
        region=region_spec,
        graph=normalized,
        output_dir=output,
        region_path=region_path,
        source_graph_path=source_graph_path,
        source_type=source_type,
        created_utc=created_utc,
        attribution=attribution,
        claim_boundary=claim_boundary,
        node_rows=node_rows,
        edge_rows=edge_rows,
        connector_rows=connector_rows,
        graph_path=graph_path,
        nodes_path=nodes_path,
        edges_path=edges_path,
        connectors_path=connectors_path,
        manifest_path=manifest_path,
    )
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest


def build_road_snapshot_manifest(
    *,
    region: RegionSpec,
    graph: nx.Graph,
    output_dir: str | Path,
    region_path: str | Path | None,
    source_graph_path: str | Path | None,
    source_type: str,
    created_utc: str | None,
    attribution: str,
    claim_boundary: str,
    node_rows: list[dict[str, Any]],
    edge_rows: list[dict[str, Any]],
    connector_rows: list[dict[str, Any]],
    graph_path: str | Path,
    nodes_path: str | Path,
    edges_path: str | Path,
    connectors_path: str | Path,
    manifest_path: str | Path,
) -> dict[str, Any]:
    """Return stable manifest metadata for road snapshot artifacts."""

    routeable_edge_count = sum(
        1 for row in edge_rows if row["routeable_vehicle_highway"] == "true"
    )
    routeable_nodes = {
        row[field]
        for row in edge_rows
        if row["routeable_vehicle_highway"] == "true"
        for field in ("u", "v")
    }
    connector_distances = [
        float(row["connector_distance_m"]) for row in connector_rows
    ]
    connector_t0 = [float(row["connector_t0_min"]) for row in connector_rows]
    outputs = {
        "graphml": _path_record(graph_path),
        "nodes_csv": _path_record(nodes_path),
        "edges_csv": _path_record(edges_path),
        "connector_audit_csv": _path_record(connectors_path),
        "manifest": {"path": _display_path(Path(manifest_path))},
    }
    return {
        "schema_version": 1,
        "result_scope": ROAD_SNAPSHOT_SCOPE,
        "claim_boundary": claim_boundary,
        "region_id": region.region_id,
        "region_label": region.label,
        "sensitivity_level": region.sensitivity_level,
        "source_type": source_type,
        "source_graph_path": _display_optional_path(source_graph_path),
        "region_path": _display_optional_path(region_path),
        "created_utc": created_utc
        or datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "boundary": boundary_record(region.boundary),
        "node_count": graph.number_of_nodes(),
        "edge_count": graph.number_of_edges(),
        "graph_type": graph.__class__.__name__,
        "routeable_node_count": len(routeable_nodes),
        "routeable_edge_count": routeable_edge_count,
        "node_table_row_count": len(node_rows),
        "edge_table_row_count": len(edge_rows),
        "connector_audit_row_count": len(connector_rows),
        "connector_audit": {
            "status_counts": _counts(row["reasonableness_status"] for row in connector_rows),
            "max_connector_distance_m": max(connector_distances) if connector_distances else 0.0,
            "max_connector_t0_min": max(connector_t0) if connector_t0 else 0.0,
        },
        "outputs": outputs,
        "attribution": attribution,
        "live_services_required_for_default_tests": False,
        "formal_acceptance_created": False,
        "can_mark_complete": False,
    }


def road_node_rows(graph: nx.Graph) -> list[dict[str, Any]]:
    """Return stable node-table rows for an OSM-like graph."""

    rows: list[dict[str, Any]] = []
    for node, data in sorted(graph.nodes(data=True), key=lambda item: repr(item[0])):
        rows.append(
            {
                "node_id": str(node),
                "x_lon": _format_float(data.get("x")),
                "y_lat": _format_float(data.get("y")),
                "source": str(data.get("source", "")),
            }
        )
    return rows


def road_edge_rows(graph: nx.Graph) -> list[dict[str, Any]]:
    """Return stable edge-table rows for an OSM-like graph."""

    rows: list[dict[str, Any]] = []
    for u, v, key, data in _iter_edges_with_keys(graph):
        highway = data.get("highway", "")
        rows.append(
            {
                "u": str(u),
                "v": str(v),
                "key": str(key),
                "realworld_edge_id": str(data.get("realworld_edge_id", "")),
                "osmid": str(data.get("osmid", "")),
                "highway": str(highway),
                "length_m": _format_float(data.get("length_m", data.get("length"))),
                "routeable_vehicle_highway": _bool_text(
                    is_routeable_vehicle_highway(highway)
                ),
                "geometry_present": _bool_text("geometry" in data),
                "source": str(data.get("source", "")),
            }
        )
    return sorted(rows, key=lambda row: (row["u"], row["v"], row["key"]))


def connector_audit_rows(
    graph: nx.Graph,
    region: Mapping[str, Any] | RegionSpec,
    *,
    ok_distance_m: float = 1_000.0,
    review_distance_m: float = 5_000.0,
) -> list[dict[str, Any]]:
    """Return connector snapping and travel-time reasonableness rows."""

    region_spec = load_region_spec(region)
    snap_graph = _routeable_graph_for_connector_audit(graph)
    role_by_point_id = {
        region_spec.primary_assembly_id: "assembly",
        region_spec.primary_destination_id: "destination",
        region_spec.rail_access_id: "rail_access",
        region_spec.rail_egress_id: "rail_egress",
    }
    snaps = snap_region_points(snap_graph, region_spec)
    rows: list[dict[str, Any]] = []
    for point_id in sorted(snaps):
        snapped = snaps[point_id]
        attrs = connector_edge_attributes(
            snapped,
            speed_kph=DEFAULT_CONNECTOR_SPEED_KPH,
            capacity=DEFAULT_CONNECTOR_CAPACITY,
            min_t0_min=MIN_CONNECTOR_T0_MIN,
        )
        rows.append(
            {
                "point_id": snapped.point_id,
                "point_role": role_by_point_id.get(snapped.point_id, "unknown"),
                "point_lat": _format_float(snapped.lat),
                "point_lon": _format_float(snapped.lon),
                "road_node": str(snapped.road_node),
                "road_lat": _format_float(snapped.road_lat),
                "road_lon": _format_float(snapped.road_lon),
                "connector_distance_m": _format_float(snapped.distance_m),
                "connector_t0_min": _format_float(attrs["t0"]),
                "connector_speed_kph": _format_float(DEFAULT_CONNECTOR_SPEED_KPH),
                "reasonableness_status": connector_reasonableness_status(
                    snapped.distance_m,
                    ok_distance_m=ok_distance_m,
                    review_distance_m=review_distance_m,
                ),
            }
        )
    return rows


def connector_reasonableness_status(
    distance_m: float,
    *,
    ok_distance_m: float = 1_000.0,
    review_distance_m: float = 5_000.0,
) -> str:
    """Classify connector distance for review triage."""

    if distance_m <= ok_distance_m:
        return "ok_connector_distance"
    if distance_m <= review_distance_m:
        return "needs_review_connector_distance"
    return "blocked_connector_distance_exceeds_threshold"


def _routeable_graph_for_connector_audit(graph: nx.Graph) -> nx.MultiDiGraph:
    """Return the routeable vehicle-road subset used for connector snapping."""

    routeable = nx.MultiDiGraph()
    routeable.graph.update(graph.graph)
    routeable.graph["filtered_by"] = "src.realworld.road_snapshot.connector_audit"
    selected_edges: list[tuple[Any, Any, Any, Mapping[str, Any]]] = [
        (u, v, key, data)
        for u, v, key, data in _iter_edges_with_keys(graph)
        if is_routeable_vehicle_highway(data.get("highway"))
    ]
    if not selected_edges:
        raise ValueError("Road snapshot has no routeable vehicle-road edges for connector audit.")
    routeable_nodes = {u for u, _, _, _ in selected_edges} | {
        v for _, v, _, _ in selected_edges
    }
    for node in sorted(routeable_nodes, key=repr):
        routeable.add_node(node, **dict(graph.nodes[node]))
    for u, v, key, data in selected_edges:
        routeable.add_edge(u, v, key=key, **dict(data))
    return routeable


def snapshot_id_for_region(region_id: str, created_utc: str | None = None) -> str:
    """Return a filesystem-safe timestamped snapshot ID for a region."""

    timestamp = created_utc or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    safe_time = re.sub(r"[^0-9A-Za-z]+", "", timestamp)
    safe_region = re.sub(r"[^0-9A-Za-z_-]+", "_", region_id).strip("_")
    return f"{safe_region}_{safe_time}"


def boundary_record(boundary: BoundarySpec) -> dict[str, Any]:
    """Return JSON-serializable boundary metadata."""

    return {
        "type": boundary.type,
        "north": boundary.north,
        "south": boundary.south,
        "east": boundary.east,
        "west": boundary.west,
        "polygon_path": boundary.polygon_path or "",
    }


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0]) if rows else []
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _iter_edges_with_keys(graph: nx.Graph) -> Iterable[tuple[Any, Any, Any, Mapping[str, Any]]]:
    if graph.is_multigraph():
        yield from graph.edges(keys=True, data=True)
        return
    for u, v, data in graph.edges(data=True):
        yield u, v, 0, data


def _path_record(path: str | Path) -> dict[str, Any]:
    candidate = Path(path)
    return {
        "path": _display_path(candidate),
        "sha256": _sha256(candidate),
        "byte_count": candidate.stat().st_size,
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _display_optional_path(path: str | Path | None) -> str:
    return "" if path is None else _display_path(Path(path))


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _format_float(value: Any) -> str:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return ""
    return f"{parsed:.6f}"


def _bool_text(value: bool) -> str:
    return "true" if value else "false"


def _counts(values: Iterable[object]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value)
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


__all__ = [
    "DEFAULT_ROAD_SNAPSHOT_ROOT",
    "ROAD_SNAPSHOT_OUTPUTS",
    "ROAD_SNAPSHOT_SCOPE",
    "boundary_record",
    "build_road_snapshot_manifest",
    "connector_audit_rows",
    "connector_reasonableness_status",
    "road_edge_rows",
    "road_node_rows",
    "snapshot_id_for_region",
    "write_road_snapshot_artifacts",
]
