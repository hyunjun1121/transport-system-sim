"""Edge-level road-attribute evidence table.

This module makes the current road-attribute contract auditable at edge level.
It separates OSM-derived values from explicit/source-backed fields, mapper
fallbacks, benchmark fields, and sensitivity-only disruption proxies. The
output is a review aid only; it does not create calibrated road overrides.
"""

from __future__ import annotations

import csv
from collections import Counter
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import networkx as nx

from .attributes import (
    HIGHWAY_DEFAULTS,
    is_routeable_vehicle_highway,
    map_osm_edge_attributes,
    normalize_highway,
    parse_length_m,
    parse_positive_float,
    parse_speed_kph,
)
from .osm_network import load_graphml
from .road_capacity_evidence import DEFAULT_CAPACITY_PER_LANE_VPH, parse_lane_count
from .road_evidence import DEFAULT_ROAD_GRAPH_PATH


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ROAD_ATTRIBUTE_EVIDENCE_PATH = (
    PROJECT_ROOT / "data" / "parameters" / "road_attribute_evidence_table.csv"
)
DEFAULT_ROAD_ATTRIBUTE_EVIDENCE_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "parameters" / "road_attribute_evidence_manifest.json"
)
ROAD_ATTRIBUTE_EVIDENCE_SCOPE = (
    "Edge-level road-attribute evidence table; not reviewed road calibration, "
    "traffic assignment validation, graph-scale acceptance, or operational "
    "routing evidence."
)
EVIDENCE_CLASSES = (
    "source-backed",
    "OSM-derived",
    "routing-engine benchmarked",
    "expert proxy",
    "sensitivity-only",
)
SOURCE_BACKED_MARKERS = frozenset(
    {
        "source-backed",
        "source_backed",
        "reviewed_source",
        "agency_source",
        "public_source",
        "reviewed",
    }
)
ROAD_ATTRIBUTE_EVIDENCE_COLUMNS: tuple[str, ...] = (
    "edge_id",
    "realworld_edge_id",
    "u",
    "v",
    "key",
    "routeable_vehicle_highway",
    "highway_raw",
    "highway_class",
    "highway_evidence_class",
    "length_m",
    "length_evidence_class",
    "maxspeed_raw",
    "observed_maxspeed_kph",
    "speed_kph_used",
    "speed_evidence_class",
    "lanes_raw",
    "lane_count",
    "lane_evidence_class",
    "capacity_raw",
    "capacity_proxy_veh_per_hr",
    "lane_based_capacity_candidate_veh_per_hr",
    "lane_based_capacity_evidence_class",
    "capacity_evidence_class",
    "free_flow_time_min",
    "free_flow_time_evidence_class",
    "base_disruption_raw",
    "base_disruption_probability",
    "base_disruption_evidence_class",
    "benchmark_travel_time_min",
    "benchmark_source_label",
    "benchmark_snapshot_path",
    "benchmark_evidence_class",
    "attribute_assumptions",
    "weak_for_final_claim",
    "evidence_status",
    "claim_boundary",
)


def build_road_attribute_evidence_rows(
    graph: nx.Graph,
    *,
    benchmark_travel_time_by_edge_id: Mapping[str, float] | None = None,
    benchmark_source_label: str = "",
    benchmark_snapshot_path: str | Path | None = None,
    capacity_per_lane_vph: float = DEFAULT_CAPACITY_PER_LANE_VPH,
) -> list[dict[str, str]]:
    """Return edge-level road-attribute evidence rows."""

    benchmark_times = dict(benchmark_travel_time_by_edge_id or {})
    capacity_per_lane_vph = _positive_float(
        capacity_per_lane_vph,
        "capacity_per_lane_vph",
    )
    rows: list[dict[str, str]] = []
    for u, v, key, data in _iter_edges_with_keys(graph):
        realworld_edge_id = _realworld_edge_id(data)
        edge_id = _edge_id(u, v, key, realworld_edge_id)
        mapped = map_osm_edge_attributes(
            data,
            edge_id=realworld_edge_id or edge_id,
        )
        highway, highway_defaulted = normalize_highway(data.get("highway"))
        length_m = parse_length_m(data.get("length_m", data.get("length")))
        observed_speed = parse_speed_kph(data.get("maxspeed"))
        lane_count = parse_lane_count(data)
        explicit_capacity = parse_positive_float(data.get("capacity"))
        explicit_disruption = _explicit_probability(
            data.get("base_p_fail", data.get("p_fail"))
        )
        benchmark_time = _benchmark_time(edge_id, realworld_edge_id, benchmark_times)

        length_evidence_class = "OSM-derived" if length_m is not None else "expert proxy"
        speed_evidence_class = "OSM-derived" if observed_speed is not None else "expert proxy"
        lane_evidence_class = "OSM-derived" if lane_count is not None else "expert proxy"
        capacity_evidence_class = _capacity_evidence_class(
            explicit_capacity=explicit_capacity,
            lane_count=lane_count,
            data=data,
        )
        lane_based_capacity_evidence_class = (
            "OSM-derived" if lane_count is not None else ""
        )
        free_flow_time_evidence_class = (
            "OSM-derived"
            if length_evidence_class == "OSM-derived"
            and speed_evidence_class == "OSM-derived"
            else "expert proxy"
        )
        base_disruption_evidence_class = (
            "source-backed"
            if explicit_disruption is not None and _has_source_backed_marker(
                data,
                ("base_p_fail_source_class", "p_fail_source_class"),
            )
            else "sensitivity-only"
        )
        benchmark_evidence_class = (
            "routing-engine benchmarked"
            if benchmark_time is not None
            and str(benchmark_source_label).strip()
            and benchmark_snapshot_path is not None
            else ""
        )
        attribute_assumptions = tuple(
            str(item) for item in mapped.get("attribute_assumptions", ())
        )
        weak_for_final_claim = any(
            evidence_class in {"expert proxy", "sensitivity-only"}
            for evidence_class in (
                length_evidence_class,
                speed_evidence_class,
                capacity_evidence_class,
                free_flow_time_evidence_class,
                base_disruption_evidence_class,
            )
        ) or bool({"capacity", "base_p_fail"} & set(attribute_assumptions))
        rows.append(
            {
                "edge_id": edge_id,
                "realworld_edge_id": realworld_edge_id,
                "u": str(u),
                "v": str(v),
                "key": str(key),
                "routeable_vehicle_highway": _bool_text(
                    is_routeable_vehicle_highway(data.get("highway"))
                ),
                "highway_raw": _raw_text(data.get("highway")),
                "highway_class": highway,
                "highway_evidence_class": (
                    "expert proxy" if highway_defaulted else "OSM-derived"
                ),
                "length_m": _fmt(length_m if length_m is not None else mapped["length_m"]),
                "length_evidence_class": length_evidence_class,
                "maxspeed_raw": _raw_text(data.get("maxspeed")),
                "observed_maxspeed_kph": _fmt(observed_speed),
                "speed_kph_used": _fmt(mapped["speed_kph"]),
                "speed_evidence_class": speed_evidence_class,
                "lanes_raw": _lane_raw_text(data),
                "lane_count": _fmt(lane_count),
                "lane_evidence_class": lane_evidence_class,
                "capacity_raw": _raw_text(data.get("capacity")),
                "capacity_proxy_veh_per_hr": _fmt(mapped["capacity"]),
                "lane_based_capacity_candidate_veh_per_hr": _fmt(
                    lane_count * capacity_per_lane_vph
                    if lane_count is not None
                    else None
                ),
                "lane_based_capacity_evidence_class": lane_based_capacity_evidence_class,
                "capacity_evidence_class": capacity_evidence_class,
                "free_flow_time_min": _fmt(mapped["t0"]),
                "free_flow_time_evidence_class": free_flow_time_evidence_class,
                "base_disruption_raw": _raw_text(
                    data.get("base_p_fail", data.get("p_fail"))
                ),
                "base_disruption_probability": _fmt(mapped["base_p_fail"]),
                "base_disruption_evidence_class": base_disruption_evidence_class,
                "benchmark_travel_time_min": _fmt(benchmark_time),
                "benchmark_source_label": str(benchmark_source_label).strip(),
                "benchmark_snapshot_path": _display_optional_path(
                    benchmark_snapshot_path
                ),
                "benchmark_evidence_class": benchmark_evidence_class,
                "attribute_assumptions": ";".join(attribute_assumptions),
                "weak_for_final_claim": _bool_text(weak_for_final_claim),
                "evidence_status": (
                    "weak_for_final_claim"
                    if weak_for_final_claim
                    else "review_ready_candidate"
                ),
                "claim_boundary": ROAD_ATTRIBUTE_EVIDENCE_SCOPE,
            }
        )
    return sorted(rows, key=lambda row: (row["u"], row["v"], row["key"], row["edge_id"]))


def build_cached_road_attribute_evidence_rows(
    path: str | Path = DEFAULT_ROAD_GRAPH_PATH,
    *,
    benchmark_travel_time_by_edge_id: Mapping[str, float] | None = None,
    benchmark_source_label: str = "",
    benchmark_snapshot_path: str | Path | None = None,
    capacity_per_lane_vph: float = DEFAULT_CAPACITY_PER_LANE_VPH,
) -> list[dict[str, str]]:
    """Load cached GraphML and return edge-level road-attribute evidence rows."""

    graph = load_graphml(path, normalize=True)
    return build_road_attribute_evidence_rows(
        graph,
        benchmark_travel_time_by_edge_id=benchmark_travel_time_by_edge_id,
        benchmark_source_label=benchmark_source_label,
        benchmark_snapshot_path=benchmark_snapshot_path,
        capacity_per_lane_vph=capacity_per_lane_vph,
    )


def write_road_attribute_evidence(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_ROAD_ATTRIBUTE_EVIDENCE_PATH,
    manifest_path: str | Path = DEFAULT_ROAD_ATTRIBUTE_EVIDENCE_MANIFEST_PATH,
    source_graph_path: str | Path = DEFAULT_ROAD_GRAPH_PATH,
    benchmark_source_label: str = "",
    benchmark_snapshot_path: str | Path | None = None,
) -> dict[str, Any]:
    """Write edge-level road-attribute table and conservative manifest."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=ROAD_ATTRIBUTE_EVIDENCE_COLUMNS,
            extrasaction="ignore",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)

    value = build_road_attribute_evidence_manifest(
        rows=rows,
        output_path=output,
        manifest_path=manifest,
        source_graph_path=source_graph_path,
        benchmark_source_label=benchmark_source_label,
        benchmark_snapshot_path=benchmark_snapshot_path,
    )
    manifest.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return value


def build_road_attribute_evidence_manifest(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path,
    manifest_path: str | Path,
    source_graph_path: str | Path,
    benchmark_source_label: str = "",
    benchmark_snapshot_path: str | Path | None = None,
) -> dict[str, Any]:
    """Return summary metadata for road-attribute evidence rows."""

    weak_count = sum(
        1 for row in rows if str(row.get("weak_for_final_claim", "")) == "true"
    )
    routeable_count = sum(
        1 for row in rows if str(row.get("routeable_vehicle_highway", "")) == "true"
    )
    return {
        "schema_version": 1,
        "result_scope": ROAD_ATTRIBUTE_EVIDENCE_SCOPE,
        "source_graph_path": _display_path(source_graph_path),
        "benchmark_source_label": str(benchmark_source_label).strip(),
        "benchmark_snapshot_path": _display_optional_path(benchmark_snapshot_path),
        "outputs": {
            "road_attribute_evidence_table": _display_path(output_path),
            "manifest": _display_path(manifest_path),
        },
        "row_count": len(rows),
        "routeable_edge_count": routeable_count,
        "weak_for_final_claim_count": weak_count,
        "evidence_status_counts": _counts(row.get("evidence_status", "") for row in rows),
        "speed_evidence_class_counts": _counts(row.get("speed_evidence_class", "") for row in rows),
        "capacity_evidence_class_counts": _counts(row.get("capacity_evidence_class", "") for row in rows),
        "lane_based_capacity_evidence_class_counts": _counts(
            row.get("lane_based_capacity_evidence_class", "") for row in rows
        ),
        "benchmark_evidence_class_counts": _counts(
            row.get("benchmark_evidence_class", "") for row in rows
        ),
        "base_disruption_evidence_class_counts": _counts(
            row.get("base_disruption_evidence_class", "") for row in rows
        ),
        "publication_ready": False,
        "formal_acceptance_created": False,
        "can_mark_complete": False,
        "claim_boundary": (
            ROAD_ATTRIBUTE_EVIDENCE_SCOPE
            + " It separates OSM-derived values, explicit/source-backed fields, "
            "fallback proxies, optional benchmark fields, and sensitivity-only "
            "disruption probabilities."
        ),
        "review_items": [
            "review edges marked weak_for_final_claim before release-scope road claims",
            "move class-level or edge-level overrides into reviewed road_class_overrides.csv only after human/source review",
            "keep BPR, traffic assignment, and operational route claims blocked until validation gates close",
        ],
    }


def _iter_edges_with_keys(graph: nx.Graph) -> Iterable[tuple[Any, Any, Any, Mapping[str, Any]]]:
    if graph.is_multigraph():
        yield from graph.edges(keys=True, data=True)
        return
    for u, v, data in graph.edges(data=True):
        yield u, v, 0, data


def _edge_id(u: Any, v: Any, key: Any, realworld_edge_id: str) -> str:
    suffix = f":{realworld_edge_id}" if realworld_edge_id else ""
    return f"{u!r}->{v!r}:{key!r}{suffix}"


def _realworld_edge_id(data: Mapping[str, Any]) -> str:
    candidate = data.get("realworld_edge_id", data.get("osmid", data.get("id")))
    if candidate is None:
        return ""
    if isinstance(candidate, (list, tuple)):
        return ",".join(str(item) for item in candidate)
    if isinstance(candidate, (set, frozenset)):
        return ",".join(sorted(str(item) for item in candidate))
    return str(candidate)


def _capacity_evidence_class(
    *,
    explicit_capacity: float | None,
    lane_count: float | None,
    data: Mapping[str, Any],
) -> str:
    if explicit_capacity is not None:
        if _has_source_backed_marker(
            data,
            ("capacity_source_class", "capacity_evidence_class"),
        ):
            return "source-backed"
        return "expert proxy"
    if lane_count is not None:
        return "expert proxy"
    return "expert proxy"


def _explicit_probability(value: Any) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if 0.0 <= parsed <= 1.0 else None


def _benchmark_time(
    edge_id: str,
    realworld_edge_id: str,
    values: Mapping[str, float],
) -> float | None:
    if edge_id not in values:
        if not realworld_edge_id or realworld_edge_id not in values:
            return None
        return _positive_float(
            values[realworld_edge_id],
            "benchmark_travel_time_min",
        )
    return _positive_float(values[edge_id], "benchmark_travel_time_min")


def _lane_raw_text(data: Mapping[str, Any]) -> str:
    values = {
        key: data.get(key)
        for key in ("lanes", "lanes:forward", "lanes:backward")
        if key in data
    }
    return ";".join(f"{key}={_raw_text(value)}" for key, value in sorted(values.items()))


def _raw_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (list, tuple)):
        return ";".join(_raw_text(item) for item in value)
    if isinstance(value, (set, frozenset)):
        return ";".join(sorted(_raw_text(item) for item in value))
    return str(value)


def _has_source_backed_marker(
    data: Mapping[str, Any],
    marker_keys: Sequence[str],
) -> bool:
    for key in marker_keys:
        values = _flatten_marker_values(data.get(key))
        if any(value in SOURCE_BACKED_MARKERS for value in values):
            return True
    return False


def _flatten_marker_values(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, (list, tuple, set, frozenset)):
        flattened: list[str] = []
        for item in value:
            flattened.extend(_flatten_marker_values(item))
        return tuple(flattened)
    return (str(value).strip().lower(),)


def _positive_float(value: Any, field_name: str) -> float:
    parsed = parse_positive_float(value)
    if parsed is None:
        raise ValueError(f"{field_name} must be positive and finite, got {value!r}")
    return parsed


def _fmt(value: Any) -> str:
    if value is None:
        return ""
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return ""
    return f"{parsed:.6f}".rstrip("0").rstrip(".")


def _bool_text(value: bool) -> str:
    return "true" if value else "false"


def _counts(values: Iterable[object]) -> dict[str, int]:
    counts: Counter[str] = Counter(str(value) for value in values)
    return dict(sorted(counts.items()))


def _display_path(path: str | Path) -> str:
    filepath = Path(path)
    try:
        return filepath.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return filepath.as_posix()


def _display_optional_path(path: str | Path | None) -> str:
    if path is None or str(path) == "":
        return ""
    return _display_path(path)


__all__ = [
    "DEFAULT_ROAD_ATTRIBUTE_EVIDENCE_MANIFEST_PATH",
    "DEFAULT_ROAD_ATTRIBUTE_EVIDENCE_PATH",
    "EVIDENCE_CLASSES",
    "ROAD_ATTRIBUTE_EVIDENCE_COLUMNS",
    "ROAD_ATTRIBUTE_EVIDENCE_SCOPE",
    "build_cached_road_attribute_evidence_rows",
    "build_road_attribute_evidence_manifest",
    "build_road_attribute_evidence_rows",
    "write_road_attribute_evidence",
]
