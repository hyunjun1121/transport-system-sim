"""Structural route evidence for graph-scope sensitivity experiments.

Only abstract canonical node IDs are emitted.  Raw path nodes, coordinates,
and geometries never leave this module; path identity is represented by a
SHA-256 digest.
"""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass, fields
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import tempfile
from typing import Any, Mapping, Sequence

import networkx as nx

from .revision_campaign import assert_isolated_output_path


CANONICAL_PUBLIC_ROAD_LEGS = (
    ("A_to_D", "A", "D"),
    ("A_to_S", "A", "S"),
    ("R_to_D", "R", "D"),
    ("S_to_R", "S", "R"),
)
DEFAULT_SCOPE_ORDER = ("top3", "top5", "top10", "full")


@dataclass(frozen=True)
class GraphScopeRouteMetric:
    """One public canonical road leg measured on one graph scope."""

    graph_scope: str
    corridor_path_count: int | None
    graph_node_count: int
    graph_edge_count: int
    leg_id: str
    source_id: str
    target_id: str
    connected: bool
    shortest_travel_time_min: float | None
    shortest_distance_m: float | None
    distance_status: str
    path_edge_count: int
    path_signature_sha256: str | None
    path_diversity_limit: int
    path_diversity_count: int
    path_diversity_status: str
    path_diversity_method: str
    full_reference_connected: bool
    full_path_edge_count: int
    full_path_edge_overlap_ratio: float | None
    full_path_edge_jaccard: float | None
    travel_time_detour_ratio_vs_full: float | None
    distance_detour_ratio_vs_full: float | None
    comparison_status: str

    def to_mapping(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CorridorTargetScopeMetric:
    """One fixed corridor target evaluated on one routing scope."""

    graph_scope: str
    corridor_path_count: int | None
    graph_node_count: int
    graph_edge_count: int
    road_multiplier: float
    selected_target_edge_count: int
    selected_target_edges_present: int
    selected_target_checksum: str
    connected: bool
    shortest_travel_time_min: float | None
    path_edge_count: int
    path_target_edge_count: int
    path_target_edge_ratio: float | None
    path_signature_sha256: str | None
    full_reference_travel_time_min: float | None
    travel_time_ratio_vs_full: float | None
    comparison_status: str

    def to_mapping(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class _RouteObservation:
    connected: bool
    travel_time_min: float | None
    distance_m: float | None
    distance_status: str
    edges: tuple[tuple[Any, Any], ...]
    signature: str | None
    diversity_count: int
    diversity_status: str
    diversity_method: str


def compute_graph_scope_route_metrics(
    graphs: Mapping[str, nx.DiGraph],
    *,
    diversity_limits: Mapping[str, int],
    legs: Sequence[tuple[str, str, str]] = CANONICAL_PUBLIC_ROAD_LEGS,
    full_scope: str = "full",
) -> tuple[GraphScopeRouteMetric, ...]:
    """Measure road structure and shortest routes against full-graph references."""

    if not isinstance(graphs, Mapping) or not graphs:
        raise ValueError("graphs must be a non-empty mapping")
    if full_scope not in graphs:
        raise ValueError(f"full reference scope {full_scope!r} is missing")
    if set(graphs) != set(diversity_limits):
        raise ValueError("diversity_limits must contain exactly the graph scopes")
    normalized_limits = {
        scope: _positive_int(limit, f"diversity_limits[{scope!r}]")
        for scope, limit in diversity_limits.items()
    }
    normalized_legs = _normalize_legs(legs)

    observations: dict[tuple[str, str], _RouteObservation] = {}
    for scope in _ordered_scopes(graphs):
        graph = graphs[scope]
        if not isinstance(graph, nx.DiGraph):
            raise TypeError(f"graph scope {scope!r} must be a networkx DiGraph")
        road = _road_view(graph)
        for leg_id, source, target in normalized_legs:
            diversity_count, diversity_status, diversity_method = (
                _reported_path_diversity(
                    graph,
                    scope=scope,
                    leg_id=leg_id,
                    limit=normalized_limits[scope],
                    full_scope=full_scope,
                )
            )
            observations[(scope, leg_id)] = _observe_route(
                road,
                source,
                target,
                diversity_count=diversity_count,
                diversity_status=diversity_status,
                diversity_method=diversity_method,
            )

    rows: list[GraphScopeRouteMetric] = []
    for scope in _ordered_scopes(graphs):
        graph = graphs[scope]
        corridor_count = _corridor_path_count(scope, graph)
        for leg_id, source, target in normalized_legs:
            current = observations[(scope, leg_id)]
            reference = observations[(full_scope, leg_id)]
            overlap, jaccard, comparison_status = _path_overlap(current, reference)
            rows.append(
                GraphScopeRouteMetric(
                    graph_scope=scope,
                    corridor_path_count=corridor_count,
                    graph_node_count=graph.number_of_nodes(),
                    graph_edge_count=graph.number_of_edges(),
                    leg_id=leg_id,
                    source_id=source,
                    target_id=target,
                    connected=current.connected,
                    shortest_travel_time_min=current.travel_time_min,
                    shortest_distance_m=current.distance_m,
                    distance_status=current.distance_status,
                    path_edge_count=len(current.edges),
                    path_signature_sha256=current.signature,
                    path_diversity_limit=normalized_limits[scope],
                    path_diversity_count=current.diversity_count,
                    path_diversity_status=current.diversity_status,
                    path_diversity_method=current.diversity_method,
                    full_reference_connected=reference.connected,
                    full_path_edge_count=len(reference.edges),
                    full_path_edge_overlap_ratio=overlap,
                    full_path_edge_jaccard=jaccard,
                    travel_time_detour_ratio_vs_full=_ratio(
                        current.travel_time_min, reference.travel_time_min
                    ),
                    distance_detour_ratio_vs_full=_ratio(
                        current.distance_m, reference.distance_m
                    ),
                    comparison_status=comparison_status,
                )
            )
    return tuple(rows)


def write_graph_scope_route_evidence(
    output_root: str | Path,
    rows: Sequence[GraphScopeRouteMetric],
    *,
    input_artifacts: Mapping[str, Mapping[str, Any]],
    claim_boundary: str = (
        "Public-data-based structural graph-scope sensitivity evidence; "
        "not field calibration or an operational route prescription."
    ),
) -> dict[str, Any]:
    """Atomically persist coordinate-free route metrics and provenance."""

    root = assert_isolated_output_path(output_root)
    root.mkdir(parents=True, exist_ok=True)
    metrics_path = assert_isolated_output_path(root / "graph_scope_route_metrics.csv")
    manifest_path = assert_isolated_output_path(
        root / "graph_scope_route_metrics_manifest.json"
    )
    normalized_rows = tuple(rows)
    if any(not isinstance(row, GraphScopeRouteMetric) for row in normalized_rows):
        raise TypeError("rows must contain GraphScopeRouteMetric values")
    _atomic_write_csv(metrics_path, normalized_rows)
    output_artifact = _artifact_record(metrics_path)
    manifest = {
        "schema_version": 2,
        "final_study_ready": False,
        "claim_boundary": str(claim_boundary),
        "contains_coordinates": False,
        "public_canonical_node_ids_only": True,
        "stage_independent": True,
        "road_mode_only": True,
        "shortest_path_weight": "t0_min",
        "distance_field": "length_m",
        "path_diversity_definition": (
            "reduced-scope candidate count copied from graph-build metadata, "
            "capped at path_diversity_limit; validation performs no path enumeration"
        ),
        "path_diversity_count_source": (
            "reduced-scope corridor_leg_candidates_json metadata"
        ),
        "path_diversity_method_field": "path_diversity_method",
        "reduced_scope_candidate_methods": sorted(
            {
                row.path_diversity_method
                for row in normalized_rows
                if row.path_diversity_method
                not in {
                    "candidate_metadata_missing",
                    "not_enumerated_cost_guard",
                }
            }
        ),
        "path_diversity_cost_guard": {
            "sentinel_count": 0,
            "status": "not_enumerated_cost_guard",
            "scopes": sorted(
                {
                    row.graph_scope
                    for row in normalized_rows
                    if row.path_diversity_status == "not_enumerated_cost_guard"
                    and row.leg_id != "S_to_R"
                }
            ),
            "legs": ["S_to_R"],
            "meaning": (
                "zero is a non-enumeration sentinel, not evidence of zero route diversity"
            ),
        },
        "overlap_definition": (
            "directed shortest-path edge intersection divided by full-path "
            "edge count; Jaccard reported separately"
        ),
        "detour_definition": "scope shortest-path value divided by full-graph value",
        "path_identity_storage": "sha256_only",
        "row_count": len(normalized_rows),
        "graph_scopes": sorted({row.graph_scope for row in normalized_rows}),
        "leg_ids": [item[0] for item in CANONICAL_PUBLIC_ROAD_LEGS],
        "input_artifacts": _json_safe(input_artifacts),
        "output_artifact": output_artifact,
        "written_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    _atomic_write_json(manifest_path, manifest)
    return {
        "metrics_path": metrics_path,
        "manifest_path": manifest_path,
        "output_artifact": output_artifact,
        "row_count": len(normalized_rows),
    }


def compute_corridor_target_scope_metrics(
    graphs: Mapping[str, nx.DiGraph],
    *,
    selected_edges: Sequence[tuple[Any, Any]],
    road_multipliers: Sequence[float],
    source: Any = "A",
    target: Any = "D",
    full_scope: str = "full",
) -> tuple[CorridorTargetScopeMetric, ...]:
    """Evaluate one fixed directed target set across routing scopes."""

    if not isinstance(graphs, Mapping) or not graphs or full_scope not in graphs:
        raise ValueError("graphs must include a full reference scope")
    normalized_edges = tuple(dict.fromkeys(tuple(edge) for edge in selected_edges))
    if not normalized_edges:
        raise ValueError("selected_edges must be non-empty")
    multipliers = tuple(float(value) for value in road_multipliers)
    if not multipliers or any(
        not math.isfinite(value) or value < 1.0 for value in multipliers
    ):
        raise ValueError("road_multipliers must contain finite values >= 1")
    if len(set(multipliers)) != len(multipliers):
        raise ValueError("road_multipliers must not contain duplicates")

    selected_set = set(normalized_edges)
    checksum = _edge_set_checksum(normalized_edges)
    observations: dict[tuple[str, float], tuple[float | None, tuple[tuple[Any, Any], ...]]] = {}
    for scope in _ordered_scopes(graphs):
        graph = graphs[scope]
        if not isinstance(graph, nx.DiGraph):
            raise TypeError(f"graph scope {scope!r} must be a networkx DiGraph")
        present = sum(graph.has_edge(*edge) for edge in normalized_edges)
        if present != len(normalized_edges):
            raise ValueError(
                f"fixed corridor target is incomplete on {scope}: "
                f"{present}/{len(normalized_edges)} edges present"
            )
        road = _road_view(graph)
        for multiplier in multipliers:
            def effective_weight(
                u: Any,
                v: Any,
                data: Mapping[str, Any],
                *,
                _multiplier: float = multiplier,
            ) -> float:
                base = float(data.get("t0"))
                return base * _multiplier if (u, v) in selected_set else base

            try:
                path = tuple(
                    nx.shortest_path(
                        road,
                        source,
                        target,
                        weight=effective_weight,
                    )
                )
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                observations[(scope, multiplier)] = (None, ())
                continue
            path_edges = tuple(zip(path, path[1:]))
            travel_time = sum(
                effective_weight(u, v, road.edges[u, v]) for u, v in path_edges
            )
            observations[(scope, multiplier)] = (travel_time, path_edges)

    rows: list[CorridorTargetScopeMetric] = []
    for scope in _ordered_scopes(graphs):
        graph = graphs[scope]
        for multiplier in multipliers:
            travel_time, path_edges = observations[(scope, multiplier)]
            full_time, _ = observations[(full_scope, multiplier)]
            target_count = sum(edge in selected_set for edge in path_edges)
            rows.append(
                CorridorTargetScopeMetric(
                    graph_scope=scope,
                    corridor_path_count=_corridor_path_count(scope, graph),
                    graph_node_count=graph.number_of_nodes(),
                    graph_edge_count=graph.number_of_edges(),
                    road_multiplier=multiplier,
                    selected_target_edge_count=len(normalized_edges),
                    selected_target_edges_present=len(normalized_edges),
                    selected_target_checksum=checksum,
                    connected=travel_time is not None,
                    shortest_travel_time_min=travel_time,
                    path_edge_count=len(path_edges),
                    path_target_edge_count=target_count,
                    path_target_edge_ratio=(
                        target_count / len(path_edges) if path_edges else None
                    ),
                    path_signature_sha256=(
                        _path_signature(path_edges) if path_edges else None
                    ),
                    full_reference_travel_time_min=full_time,
                    travel_time_ratio_vs_full=_ratio(travel_time, full_time),
                    comparison_status=(
                        "comparable" if travel_time is not None and full_time is not None
                        else "unreachable"
                    ),
                )
            )
    return tuple(rows)


def write_corridor_target_scope_evidence(
    output_root: str | Path,
    rows: Sequence[CorridorTargetScopeMetric],
    *,
    input_artifacts: Mapping[str, Mapping[str, Any]],
    claim_boundary: str = (
        "Fixed corridor-envelope target response for graph-scope sensitivity; "
        "not observed damage, field calibration, or route prescription."
    ),
) -> dict[str, Any]:
    """Persist coordinate-free fixed-target route response and hashes."""

    root = assert_isolated_output_path(output_root)
    root.mkdir(parents=True, exist_ok=True)
    metrics_path = assert_isolated_output_path(
        root / "corridor_target_scope_metrics.csv"
    )
    manifest_path = assert_isolated_output_path(
        root / "corridor_target_scope_metrics_manifest.json"
    )
    normalized_rows = tuple(rows)
    if not normalized_rows or any(
        not isinstance(row, CorridorTargetScopeMetric) for row in normalized_rows
    ):
        raise TypeError("rows must contain CorridorTargetScopeMetric values")
    checksums = {row.selected_target_checksum for row in normalized_rows}
    if len(checksums) != 1:
        raise ValueError("corridor target checksum must be fixed across scopes")
    _atomic_write_csv(
        metrics_path,
        normalized_rows,
        record_type=CorridorTargetScopeMetric,
    )
    output_artifact = _artifact_record(metrics_path)
    manifest = {
        "schema_version": 1,
        "final_study_ready": False,
        "claim_boundary": str(claim_boundary),
        "contains_coordinates": False,
        "public_canonical_node_ids_only": True,
        "fixed_target_across_scopes": True,
        "dynamic_rerouting_reflected_by_shortest_path": True,
        "shortest_path_weight": "t0_min_times_fixed_target_multiplier",
        "selected_target_checksum": next(iter(checksums)),
        "selected_target_edge_count": normalized_rows[0].selected_target_edge_count,
        "row_count": len(normalized_rows),
        "graph_scopes": sorted({row.graph_scope for row in normalized_rows}),
        "road_multipliers": sorted({row.road_multiplier for row in normalized_rows}),
        "input_artifacts": _json_safe(input_artifacts),
        "output_artifact": output_artifact,
        "written_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    _atomic_write_json(manifest_path, manifest)
    return {
        "metrics_path": metrics_path,
        "manifest_path": manifest_path,
        "output_artifact": output_artifact,
        "row_count": len(normalized_rows),
    }


def _observe_route(
    road: nx.DiGraph,
    source: str,
    target: str,
    *,
    diversity_count: int,
    diversity_status: str,
    diversity_method: str,
) -> _RouteObservation:
    try:
        path = tuple(nx.shortest_path(road, source, target, weight="t0"))
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return _RouteObservation(
            False,
            None,
            None,
            "unreachable",
            (),
            None,
            diversity_count,
            diversity_status,
            diversity_method,
        )
    edges = tuple(zip(path, path[1:]))
    travel_time = sum(float(road.edges[edge]["t0"]) for edge in edges)
    distance, distance_status = _path_distance(road, edges)
    return _RouteObservation(
        True,
        travel_time,
        distance,
        distance_status,
        edges,
        _path_signature(edges),
        diversity_count,
        diversity_status,
        diversity_method,
    )


def _reported_path_diversity(
    graph: nx.DiGraph,
    *,
    scope: str,
    leg_id: str,
    limit: int,
    full_scope: str,
) -> tuple[int, str, str]:
    """Read build-time candidate counts without enumerating graph paths.

    Full-graph and S-to-R enumeration is intentionally skipped.  Their zero
    count is a cost-guard sentinel whose status/method prevents interpretation
    as observed zero path diversity.
    """

    if scope == full_scope or leg_id == "S_to_R":
        return 0, "not_enumerated_cost_guard", "not_enumerated_cost_guard"

    metadata = _candidate_path_metadata(graph)
    item = metadata.get(leg_id)
    if not isinstance(item, Mapping):
        return 0, "candidate_metadata_missing", "candidate_metadata_missing"
    count = item.get("candidate_count")
    method = item.get("method")
    if (
        isinstance(count, bool)
        or not isinstance(count, int)
        or count < 0
        or not isinstance(method, str)
        or not method.strip()
    ):
        return 0, "candidate_metadata_missing", "candidate_metadata_missing"
    reported = min(count, limit)
    status = "capped_at_limit" if count >= limit else "exhausted_before_limit"
    return reported, status, method.strip()


def _candidate_path_metadata(graph: nx.DiGraph) -> Mapping[str, Any]:
    raw = graph.graph.get("corridor_leg_candidates_json")
    if isinstance(raw, Mapping):
        return raw
    if not isinstance(raw, str) or not raw.strip():
        return {}
    try:
        value = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return {}
    return value if isinstance(value, Mapping) else {}


def _path_distance(
    graph: nx.DiGraph, edges: Sequence[tuple[Any, Any]]
) -> tuple[float | None, str]:
    distance = 0.0
    for edge in edges:
        value = graph.edges[edge].get("length_m")
        try:
            number = float(value)
        except (TypeError, ValueError):
            return None, "missing_or_invalid_length_m"
        if not math.isfinite(number) or number < 0.0:
            return None, "missing_or_invalid_length_m"
        distance += number
    return distance, "available"


def _path_overlap(
    current: _RouteObservation,
    reference: _RouteObservation,
) -> tuple[float | None, float | None, str]:
    if not reference.connected:
        return None, None, "full_reference_unreachable"
    if not current.connected:
        return None, None, "scope_unreachable"
    current_edges = set(current.edges)
    reference_edges = set(reference.edges)
    intersection = len(current_edges.intersection(reference_edges))
    union = len(current_edges.union(reference_edges))
    overlap = intersection / len(reference_edges) if reference_edges else 1.0
    jaccard = intersection / union if union else 1.0
    return overlap, jaccard, "available"


def _ratio(
    numerator: float | None, denominator: float | None
) -> float | None:
    if numerator is None or denominator is None or denominator <= 0.0:
        return None
    return numerator / denominator


def _road_view(graph: nx.DiGraph) -> nx.DiGraph:
    return nx.subgraph_view(
        graph,
        filter_edge=lambda u, v: graph.edges[u, v].get("mode", "road") == "road",
    )


def _path_signature(edges: Sequence[tuple[Any, Any]]) -> str:
    payload = json.dumps(
        [[str(source), str(target)] for source, target in edges],
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _edge_set_checksum(edges: Sequence[tuple[Any, Any]]) -> str:
    normalized = sorted({(str(source), str(target)) for source, target in edges})
    payload = json.dumps(
        normalized,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _corridor_path_count(scope: str, graph: nx.DiGraph) -> int | None:
    if scope == "full":
        return None
    value = graph.graph.get("corridor_path_count")
    if value is None and scope.startswith("top"):
        try:
            value = int(scope[3:])
        except ValueError:
            return None
    if isinstance(value, bool) or value is None:
        return None
    try:
        normalized = int(value)
    except (TypeError, ValueError):
        return None
    return normalized if normalized > 0 else None


def _ordered_scopes(graphs: Mapping[str, nx.DiGraph]) -> tuple[str, ...]:
    rank = {scope: index for index, scope in enumerate(DEFAULT_SCOPE_ORDER)}
    return tuple(sorted(graphs, key=lambda scope: (rank.get(scope, len(rank)), scope)))


def _normalize_legs(
    legs: Sequence[tuple[str, str, str]],
) -> tuple[tuple[str, str, str], ...]:
    normalized = tuple(tuple(str(value) for value in leg) for leg in legs)
    if not normalized or any(len(leg) != 3 or not all(leg) for leg in normalized):
        raise ValueError("legs must contain non-empty (leg_id, source, target) tuples")
    if len({leg[0] for leg in normalized}) != len(normalized):
        raise ValueError("leg IDs must be unique")
    return normalized


def _positive_int(value: Any, path: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{path} must be a positive integer")
    return value


def _atomic_write_csv(
    path: Path,
    rows: Sequence[Any],
    *,
    record_type: type[Any] = GraphScopeRouteMetric,
) -> None:
    field_names = [item.name for item in fields(record_type)]
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent, prefix=f".{path.name}.", suffix=".tmp"
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=field_names, extrasaction="raise")
            writer.writeheader()
            for row in rows:
                writer.writerow(row.to_mapping())
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def _atomic_write_json(path: Path, value: Mapping[str, Any]) -> None:
    payload = (
        json.dumps(
            _json_safe(value),
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=path.parent, prefix=f".{path.name}.", suffix=".tmp"
    )
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def _artifact_record(path: Path) -> dict[str, Any]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
            size += len(chunk)
    return {"path": str(path), "sha256": digest.hexdigest(), "size_bytes": size}


def _json_safe(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


__all__ = [
    "CANONICAL_PUBLIC_ROAD_LEGS",
    "DEFAULT_SCOPE_ORDER",
    "GraphScopeRouteMetric",
    "compute_graph_scope_route_metrics",
    "write_graph_scope_route_evidence",
]
