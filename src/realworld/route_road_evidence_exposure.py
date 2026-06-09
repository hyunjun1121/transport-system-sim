"""Route-level exposure of road-evidence gaps.

This module links current road-class evidence gaps to the canonical pilot
routes used for graph-scale review. It is a reviewer aid only: it does not
calibrate road speeds, capacities, disruption probabilities, or route choice.
"""

from __future__ import annotations

import csv
import json
from math import isfinite
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import networkx as nx

from src.realworld.road_evidence_review_packet import (
    DEFAULT_ROAD_EVIDENCE_REVIEW_PACKET_PATH,
    ROAD_EVIDENCE_REVIEW_PACKET_SCOPE,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CURRENT_ALTERNATE_ROUTES_PATH = (
    PROJECT_ROOT / "data" / "validation" / "graph_scale_alternate_routes.csv"
)
DEFAULT_MULTI_CORRIDOR_ROUTES_PATH = (
    PROJECT_ROOT / "data" / "validation" / "graph_scale_multi_corridor_routes.csv"
)
DEFAULT_ROUTE_ROAD_EVIDENCE_EXPOSURE_PATH = (
    PROJECT_ROOT / "data" / "validation" / "canonical_route_road_evidence_exposure.csv"
)
DEFAULT_ROUTE_ROAD_EVIDENCE_EXPOSURE_SUMMARY_PATH = (
    PROJECT_ROOT / "data" / "validation" / "canonical_route_road_evidence_exposure_summary.md"
)
DEFAULT_ROUTE_ROAD_EVIDENCE_EXPOSURE_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "validation" / "canonical_route_road_evidence_exposure_manifest.json"
)

ROUTE_ROAD_EVIDENCE_EXPOSURE_SCOPE = (
    "Canonical route road-evidence exposure review aid; not accepted road "
    "calibration, not benchmark validation, not graph-scale acceptance, and "
    "not operational routing evidence."
)

ROUTE_ROAD_EVIDENCE_EXPOSURE_COLUMNS: tuple[str, ...] = (
    "region_id",
    "route_check_id",
    "route_label",
    "graph_variant",
    "route_rank",
    "source",
    "target",
    "route_available",
    "exact_full_path_present_in_analysis",
    "route_status",
    "path_edge_count",
    "highway",
    "edge_count",
    "distance_m",
    "time_min",
    "distance_share",
    "time_share",
    "speed_evidence_status",
    "capacity_evidence_status",
    "base_disruption_evidence_status",
    "override_source_class",
    "review_priority",
    "weak_for_final_claim",
    "candidate_artifacts",
    "publication_use_status",
    "claim_scope",
    "notes",
)

GRAPH_VARIANTS: tuple[tuple[str, Path], ...] = (
    ("current_reduced_corridor", DEFAULT_CURRENT_ALTERNATE_ROUTES_PATH),
    ("multi_corridor_candidate", DEFAULT_MULTI_CORRIDOR_ROUTES_PATH),
)


def build_route_road_evidence_exposure_rows(
    graph: nx.DiGraph,
    *,
    road_evidence_review_path: str | Path = DEFAULT_ROAD_EVIDENCE_REVIEW_PACKET_PATH,
    graph_variant_paths: Sequence[tuple[str, str | Path]] = GRAPH_VARIANTS,
) -> list[dict[str, str]]:
    """Return road-evidence exposure rows for canonical route candidates."""

    evidence_by_highway = _load_road_evidence_by_highway(road_evidence_review_path)
    rows: list[dict[str, str]] = []
    seen: set[tuple[str, str, str, str]] = set()
    for graph_variant, path in graph_variant_paths:
        for route_row in _read_route_rows(path):
            route_key = (
                graph_variant,
                route_row.get("route_check_id", ""),
                route_row.get("full_route_rank", ""),
                route_row.get("full_path_nodes", ""),
            )
            if route_key in seen:
                continue
            seen.add(route_key)
            rows.extend(
                _exposure_rows_for_route(
                    graph,
                    route_row=route_row,
                    graph_variant=graph_variant,
                    evidence_by_highway=evidence_by_highway,
                )
            )

    rows.sort(
        key=lambda row: (
            row["graph_variant"],
            row["route_check_id"],
            _int(row["route_rank"]),
            -_float(row["distance_share"]),
            row["highway"],
        )
    )
    return rows


def write_route_road_evidence_exposure(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_ROUTE_ROAD_EVIDENCE_EXPOSURE_PATH,
    summary_path: str | Path = DEFAULT_ROUTE_ROAD_EVIDENCE_EXPOSURE_SUMMARY_PATH,
    manifest_path: str | Path = DEFAULT_ROUTE_ROAD_EVIDENCE_EXPOSURE_MANIFEST_PATH,
    road_evidence_review_path: str | Path = DEFAULT_ROAD_EVIDENCE_REVIEW_PACKET_PATH,
    graph_variant_paths: Sequence[tuple[str, str | Path]] = GRAPH_VARIANTS,
) -> dict[str, Any]:
    """Write route-level exposure rows, summary, and manifest."""

    output = Path(output_path)
    summary = Path(summary_path)
    manifest = Path(manifest_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=ROUTE_ROAD_EVIDENCE_EXPOSURE_COLUMNS,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)

    value = summarize_route_road_evidence_exposure(
        rows,
        output_path=output,
        summary_path=summary,
        manifest_path=manifest,
        road_evidence_review_path=road_evidence_review_path,
        graph_variant_paths=graph_variant_paths,
    )
    summary.write_text(_summary_text(value), encoding="utf-8")
    with manifest.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return value


def summarize_route_road_evidence_exposure(
    rows: Sequence[Mapping[str, str]],
    *,
    output_path: str | Path = DEFAULT_ROUTE_ROAD_EVIDENCE_EXPOSURE_PATH,
    summary_path: str | Path = DEFAULT_ROUTE_ROAD_EVIDENCE_EXPOSURE_SUMMARY_PATH,
    manifest_path: str | Path = DEFAULT_ROUTE_ROAD_EVIDENCE_EXPOSURE_MANIFEST_PATH,
    road_evidence_review_path: str | Path = DEFAULT_ROAD_EVIDENCE_REVIEW_PACKET_PATH,
    graph_variant_paths: Sequence[tuple[str, str | Path]] = GRAPH_VARIANTS,
) -> dict[str, Any]:
    """Return conservative manifest values for route exposure rows."""

    weak_rows = [
        row
        for row in rows
        if str(row.get("weak_for_final_claim", "")).strip().lower() == "true"
    ]
    route_candidates = {
        (
            row.get("graph_variant", ""),
            row.get("route_check_id", ""),
            row.get("route_rank", ""),
        )
        for row in rows
    }
    weak_distance_share_by_variant = {}
    for variant in sorted({row.get("graph_variant", "") for row in rows}):
        variant_rows = [row for row in rows if row.get("graph_variant", "") == variant]
        weak_distance_share_by_variant[variant] = _round(
            sum(
                _float(row.get("distance_share"))
                for row in variant_rows
                if str(row.get("weak_for_final_claim", "")).lower() == "true"
            )
        )
    return {
        "schema_version": 1,
        "result_scope": ROUTE_ROAD_EVIDENCE_EXPOSURE_SCOPE,
        "inputs": {
            "road_evidence_review_packet": _display_path(road_evidence_review_path),
            "graph_variant_route_tables": {
                variant: _display_path(path) for variant, path in graph_variant_paths
            },
        },
        "outputs": {
            "route_road_evidence_exposure": _display_path(output_path),
            "summary": _display_path(summary_path),
            "manifest": _display_path(manifest_path),
        },
        "row_count": len(rows),
        "route_candidate_count": len(route_candidates),
        "route_count": _unique_count(row.get("route_check_id", "") for row in rows),
        "graph_variant_counts": _counts(row.get("graph_variant", "") for row in rows),
        "route_status_counts": _counts(row.get("route_status", "") for row in rows),
        "highway_counts": _counts(row.get("highway", "") for row in rows),
        "weak_for_final_claim_count": len(weak_rows),
        "weak_distance_share_sum_by_variant": weak_distance_share_by_variant,
        "publication_ready": False,
        "acceptance_ready": False,
        "claim_boundary": (
            "This artifact links current weak road-evidence classes to "
            "canonical route candidates. It does not create reviewed road "
            "inputs, calibrated traffic behavior, validation acceptance, "
            "graph-scale acceptance, or operational routing claims."
        ),
        "review_items": [
            "prioritize reviewed road evidence for weak classes that dominate canonical route distance or time",
            "review connector exposure separately from OSM road-class calibration",
            "rerun this exposure after road-class overrides, OSM cache, or graph-scale method changes",
            "use this artifact as validation and road-evidence review support only",
        ],
    }


def _exposure_rows_for_route(
    graph: nx.DiGraph,
    *,
    route_row: Mapping[str, str],
    graph_variant: str,
    evidence_by_highway: Mapping[str, Mapping[str, str]],
) -> list[dict[str, str]]:
    nodes = _path_nodes(route_row.get("full_path_nodes", ""))
    edges = tuple(zip(nodes, nodes[1:]))
    if not edges:
        return [_missing_route_row(route_row, graph_variant)]

    aggregates: dict[str, dict[str, Any]] = {}
    total_distance = 0.0
    total_time = 0.0
    for u, v in edges:
        if not graph.has_edge(u, v):
            highway = "missing_edge"
            length_m = 0.0
            time_min = 0.0
            edge_id = f"{u}->{v}"
            override_source_class = ""
        else:
            data = graph.edges[u, v]
            highway = str(data.get("highway", "unknown") or "unknown")
            length_m = _finite_float(data.get("length_m")) or 0.0
            time_min = _finite_float(data.get("t0")) or 0.0
            edge_id = str(data.get("realworld_edge_id", f"{u}->{v}"))
            override_source_class = str(
                data.get("road_class_override_source_class", "")
            ).strip()
        total_distance += length_m
        total_time += time_min
        bucket = aggregates.setdefault(
            highway,
            {
                "edge_count": 0,
                "distance_m": 0.0,
                "time_min": 0.0,
                "edge_ids": [],
                "override_source_classes": set(),
            },
        )
        bucket["edge_count"] += 1
        bucket["distance_m"] += length_m
        bucket["time_min"] += time_min
        bucket["edge_ids"].append(edge_id)
        if override_source_class:
            bucket["override_source_classes"].add(override_source_class)

    rows: list[dict[str, str]] = []
    for highway, aggregate in aggregates.items():
        evidence = _evidence_for_highway(highway, evidence_by_highway)
        weak = _weak_for_final_claim(highway, evidence)
        edge_override_source_class = _edge_override_source_class(aggregate)
        override_source_class = edge_override_source_class or str(
            evidence.get("override_source_class", "")
        )
        rows.append(
            {
                "region_id": str(route_row.get("region_id", "")),
                "route_check_id": str(route_row.get("route_check_id", "")),
                "route_label": str(route_row.get("route_label", "")),
                "graph_variant": graph_variant,
                "route_rank": str(route_row.get("full_route_rank", "")),
                "source": str(route_row.get("source", "")),
                "target": str(route_row.get("target", "")),
                "route_available": str(route_row.get("full_path_available", "")).lower(),
                "exact_full_path_present_in_analysis": str(
                    route_row.get("exact_full_path_present_in_analysis", "")
                ).lower(),
                "route_status": str(route_row.get("status", "")),
                "path_edge_count": str(len(edges)),
                "highway": highway,
                "edge_count": str(aggregate["edge_count"]),
                "distance_m": _fmt(aggregate["distance_m"]),
                "time_min": _fmt(aggregate["time_min"]),
                "distance_share": _fmt(_ratio(aggregate["distance_m"], total_distance)),
                "time_share": _fmt(_ratio(aggregate["time_min"], total_time)),
                "speed_evidence_status": evidence.get("speed_evidence_status", ""),
                "capacity_evidence_status": evidence.get("capacity_evidence_status", ""),
                "base_disruption_evidence_status": evidence.get(
                    "base_disruption_evidence_status", ""
                ),
                "override_source_class": override_source_class,
                "review_priority": evidence.get("review_priority", "route_only"),
                "weak_for_final_claim": str(weak).lower(),
                "candidate_artifacts": evidence.get("candidate_artifacts", ""),
                "publication_use_status": (
                    "route_exposure_review_support_only_not_acceptance"
                ),
                "claim_scope": ROUTE_ROAD_EVIDENCE_EXPOSURE_SCOPE,
                "notes": _notes(
                    highway,
                    aggregate["edge_ids"],
                    weak,
                    edge_override_source_class=edge_override_source_class,
                ),
            }
        )
    return rows


def _missing_route_row(
    route_row: Mapping[str, str],
    graph_variant: str,
) -> dict[str, str]:
    return {
        "region_id": str(route_row.get("region_id", "")),
        "route_check_id": str(route_row.get("route_check_id", "")),
        "route_label": str(route_row.get("route_label", "")),
        "graph_variant": graph_variant,
        "route_rank": str(route_row.get("full_route_rank", "")),
        "source": str(route_row.get("source", "")),
        "target": str(route_row.get("target", "")),
        "route_available": "false",
        "exact_full_path_present_in_analysis": "false",
        "route_status": "missing_route",
        "path_edge_count": "0",
        "highway": "",
        "edge_count": "0",
        "distance_m": "",
        "time_min": "",
        "distance_share": "",
        "time_share": "",
        "speed_evidence_status": "",
        "capacity_evidence_status": "",
        "base_disruption_evidence_status": "",
        "override_source_class": "",
        "review_priority": "high",
        "weak_for_final_claim": "true",
        "candidate_artifacts": "",
        "publication_use_status": "route_missing_review_required",
        "claim_scope": ROUTE_ROAD_EVIDENCE_EXPOSURE_SCOPE,
        "notes": "route candidate has no parseable full_path_nodes value",
    }


def _evidence_for_highway(
    highway: str,
    evidence_by_highway: Mapping[str, Mapping[str, str]],
) -> Mapping[str, str]:
    if highway in evidence_by_highway:
        return evidence_by_highway[highway]
    if highway == "connector":
        return {
            "speed_evidence_status": "connector_geometry_sanity_only",
            "capacity_evidence_status": "connector_capacity_assumption",
            "base_disruption_evidence_status": "connector_base_p_fail_zero_assumption",
            "override_source_class": "connector assumption",
            "review_priority": "route_connector_review",
            "weak_for_final_claim": "true",
            "candidate_artifacts": "data/validation/route_plausibility.csv",
        }
    return {
        "speed_evidence_status": "missing_route_level_road_evidence",
        "capacity_evidence_status": "missing_route_level_road_evidence",
        "base_disruption_evidence_status": "missing_route_level_road_evidence",
        "override_source_class": "",
        "review_priority": "route_only",
        "weak_for_final_claim": "true",
        "candidate_artifacts": ROAD_EVIDENCE_REVIEW_PACKET_SCOPE,
    }


def _weak_for_final_claim(
    highway: str,
    evidence: Mapping[str, str],
) -> bool:
    if highway == "connector":
        return True
    return str(evidence.get("weak_for_final_claim", "true")).strip().lower() == "true"


def _edge_override_source_class(
    aggregate: Mapping[str, Any],
) -> str:
    edge_classes = {
        str(item).strip()
        for item in aggregate.get("override_source_classes", set())
        if str(item).strip()
    }
    return ";".join(sorted(edge_classes))


def _load_road_evidence_by_highway(
    path: str | Path,
) -> dict[str, dict[str, str]]:
    rows = _read_csv_rows(path)
    return {
        str(row.get("highway", "")).strip(): {
            str(key): str(value or "") for key, value in row.items()
        }
        for row in rows
        if str(row.get("highway", "")).strip()
    }


def _read_route_rows(path: str | Path) -> list[dict[str, str]]:
    return _read_csv_rows(path)


def _read_csv_rows(path: str | Path) -> list[dict[str, str]]:
    csv_path = Path(path)
    if not csv_path.exists():
        return []
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _path_nodes(value: str) -> tuple[str, ...]:
    return tuple(part for part in str(value or "").split(">") if part)


def _notes(
    highway: str,
    edge_ids: Sequence[str],
    weak: bool,
    *,
    edge_override_source_class: str = "",
) -> str:
    sample = ";".join(edge_ids[:3])
    suffix = "" if len(edge_ids) <= 3 else f"; plus {len(edge_ids) - 3} more"
    if highway == "connector":
        prefix = "connector exposure should be reviewed with snapping distances"
    elif weak:
        prefix = "weak road-evidence exposure on this route class"
    else:
        prefix = "route class has stronger review-packet evidence status"
    override_note = (
        ""
        if not edge_override_source_class
        else f"; edge_override_source_class={edge_override_source_class}"
    )
    return f"{prefix}; sample_edges={sample}{suffix}{override_note}"


def _summary_text(value: Mapping[str, Any]) -> str:
    lines = [
        "# Canonical Route Road-Evidence Exposure",
        "",
        "This artifact links current road-evidence gaps to canonical route",
        "candidates used in graph-scale review. It is review support only and",
        "does not accept road calibration, validation, graph-scale strategy, or",
        "operational routing claims.",
        "",
        "## Current Snapshot",
        "",
        f"- Row count: {value['row_count']}",
        f"- Route candidates: {value['route_candidate_count']}",
        f"- Routes: {value['route_count']}",
        f"- Weak exposure rows: {value['weak_for_final_claim_count']}",
        f"- Graph variants: {_counts_text(value['graph_variant_counts'])}",
        f"- Highway rows: {_counts_text(value['highway_counts'])}",
        "",
        "## Review Items",
        "",
    ]
    for item in value["review_items"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            str(value["claim_boundary"]),
            "",
        ]
    )
    return "\n".join(lines)


def _counts(values: Iterable[object]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value).strip()
        if not key:
            continue
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _unique_count(values: Iterable[object]) -> int:
    return len({str(value).strip() for value in values if str(value).strip()})


def _counts_text(values: Mapping[str, Any]) -> str:
    return "; ".join(f"{key}={values[key]}" for key in sorted(values))


def _finite_float(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if isfinite(parsed) else None


def _ratio(value: float, total: float) -> float:
    if total <= 0.0:
        return 0.0
    return value / total


def _float(value: object) -> float:
    parsed = _finite_float(value)
    return 0.0 if parsed is None else parsed


def _int(value: object) -> int:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return 0


def _round(value: float) -> float:
    return round(value, 6)


def _fmt(value: float | None) -> str:
    if value is None or not isfinite(value):
        return ""
    return f"{value:.6f}"


def _display_path(path: str | Path) -> str:
    filepath = Path(path)
    try:
        return filepath.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return filepath.as_posix()


__all__ = [
    "DEFAULT_CURRENT_ALTERNATE_ROUTES_PATH",
    "DEFAULT_MULTI_CORRIDOR_ROUTES_PATH",
    "DEFAULT_ROUTE_ROAD_EVIDENCE_EXPOSURE_MANIFEST_PATH",
    "DEFAULT_ROUTE_ROAD_EVIDENCE_EXPOSURE_PATH",
    "DEFAULT_ROUTE_ROAD_EVIDENCE_EXPOSURE_SUMMARY_PATH",
    "GRAPH_VARIANTS",
    "ROUTE_ROAD_EVIDENCE_EXPOSURE_COLUMNS",
    "ROUTE_ROAD_EVIDENCE_EXPOSURE_SCOPE",
    "build_route_road_evidence_exposure_rows",
    "summarize_route_road_evidence_exposure",
    "write_route_road_evidence_exposure",
]
