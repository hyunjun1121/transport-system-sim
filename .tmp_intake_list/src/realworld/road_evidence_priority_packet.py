"""Road evidence priority packet.

The road evidence review packet lists class-level evidence gaps, while the
route exposure packet shows which weak classes appear on canonical route
candidates. This module joins those views so reviewers can prioritize speed,
capacity, disruption, connector, and override evidence collection without
creating accepted road inputs.
"""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from src.realworld.road_evidence_review_packet import (
    DEFAULT_ROAD_EVIDENCE_REVIEW_PACKET_PATH,
)
from src.realworld.road_source_readiness_packet import (
    DEFAULT_ROAD_SOURCE_READINESS_PACKET_PATH,
)
from src.realworld.route_road_evidence_exposure import (
    DEFAULT_ROUTE_ROAD_EVIDENCE_EXPOSURE_MANIFEST_PATH,
    DEFAULT_ROUTE_ROAD_EVIDENCE_EXPOSURE_PATH,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ROAD_EVIDENCE_PRIORITY_PACKET_PATH = (
    PROJECT_ROOT / "data" / "road" / "road_evidence_priority_packet.csv"
)
DEFAULT_ROAD_EVIDENCE_PRIORITY_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "road" / "road_evidence_priority_manifest.json"
)
DEFAULT_ROAD_EVIDENCE_PRIORITY_DOC_PATH = (
    PROJECT_ROOT / "docs" / "road_evidence_priority_packet.md"
)
ROAD_EVIDENCE_PRIORITY_SCOPE = (
    "Road evidence priority packet only; not reviewed road-class overrides, "
    "not calibrated traffic evidence, not graph-scale acceptance, not "
    "validation acceptance, and not operational routing evidence."
)
ROAD_EVIDENCE_PRIORITY_COLUMNS: tuple[str, ...] = (
    "highway",
    "review_priority",
    "priority_status",
    "routeable_edge_count",
    "routeable_length_km",
    "routeable_length_share",
    "canonical_exposure_rows",
    "exposed_route_count",
    "exposed_route_candidate_count",
    "exposed_graph_variants",
    "route_status_counts",
    "total_exposed_distance_m",
    "total_exposed_time_min",
    "max_route_time_share",
    "speed_evidence_status",
    "capacity_evidence_status",
    "base_disruption_evidence_status",
    "override_source_class",
    "needed_source_requests",
    "candidate_artifacts",
    "required_reviewer_action",
    "publication_use_status",
    "can_support_road_evidence_gate",
    "claim_boundary",
)


def build_road_evidence_priority_rows(
    *,
    road_evidence_review_path: str | Path = DEFAULT_ROAD_EVIDENCE_REVIEW_PACKET_PATH,
    route_exposure_path: str | Path = DEFAULT_ROUTE_ROAD_EVIDENCE_EXPOSURE_PATH,
    route_exposure_manifest_path: str | Path = (
        DEFAULT_ROUTE_ROAD_EVIDENCE_EXPOSURE_MANIFEST_PATH
    ),
    road_source_readiness_path: str | Path = DEFAULT_ROAD_SOURCE_READINESS_PACKET_PATH,
) -> list[dict[str, str]]:
    """Return road-class priority rows from evidence and route exposure packets."""

    road_rows = {
        row.get("highway", ""): row
        for row in _read_csv_rows(road_evidence_review_path)
        if row.get("highway", "")
    }
    exposure_rows = _read_csv_rows(route_exposure_path)
    source_request_ids = {
        row.get("request_id", "")
        for row in _read_csv_rows(road_source_readiness_path)
        if row.get("request_id", "")
    }
    exposure_by_highway = _aggregate_exposure(exposure_rows)
    highways = sorted(set(road_rows) | set(exposure_by_highway))
    rows = [
        _priority_row(
            highway,
            road_rows.get(highway, {}),
            exposure_by_highway.get(highway, _empty_exposure()),
            source_request_ids=source_request_ids,
            route_exposure_artifacts=(
                _display_path(route_exposure_path),
                _display_path(route_exposure_manifest_path),
            ),
        )
        for highway in highways
    ]
    rows.sort(key=_priority_sort_key)
    return rows


def write_road_evidence_priority_packet(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_ROAD_EVIDENCE_PRIORITY_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_ROAD_EVIDENCE_PRIORITY_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_ROAD_EVIDENCE_PRIORITY_DOC_PATH,
    road_evidence_review_path: str | Path = DEFAULT_ROAD_EVIDENCE_REVIEW_PACKET_PATH,
    route_exposure_path: str | Path = DEFAULT_ROUTE_ROAD_EVIDENCE_EXPOSURE_PATH,
    route_exposure_manifest_path: str | Path = (
        DEFAULT_ROUTE_ROAD_EVIDENCE_EXPOSURE_MANIFEST_PATH
    ),
    road_source_readiness_path: str | Path = DEFAULT_ROAD_SOURCE_READINESS_PACKET_PATH,
) -> dict[str, Any]:
    """Write road evidence priority CSV, manifest, and Markdown."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=ROAD_EVIDENCE_PRIORITY_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {column: str(row.get(column, "")) for column in ROAD_EVIDENCE_PRIORITY_COLUMNS}
            )

    summary = build_road_evidence_priority_manifest(
        rows=rows,
        output_path=output,
        manifest_path=manifest,
        doc_path=doc,
        road_evidence_review_path=road_evidence_review_path,
        route_exposure_path=route_exposure_path,
        route_exposure_manifest_path=route_exposure_manifest_path,
        road_source_readiness_path=road_source_readiness_path,
    )
    manifest.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    doc.write_text(
        build_road_evidence_priority_markdown(summary, rows=rows),
        encoding="utf-8",
    )
    return summary


def build_road_evidence_priority_manifest(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_ROAD_EVIDENCE_PRIORITY_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_ROAD_EVIDENCE_PRIORITY_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_ROAD_EVIDENCE_PRIORITY_DOC_PATH,
    road_evidence_review_path: str | Path = DEFAULT_ROAD_EVIDENCE_REVIEW_PACKET_PATH,
    route_exposure_path: str | Path = DEFAULT_ROUTE_ROAD_EVIDENCE_EXPOSURE_PATH,
    route_exposure_manifest_path: str | Path = (
        DEFAULT_ROUTE_ROAD_EVIDENCE_EXPOSURE_MANIFEST_PATH
    ),
    road_source_readiness_path: str | Path = DEFAULT_ROAD_SOURCE_READINESS_PACKET_PATH,
) -> dict[str, Any]:
    """Return a conservative manifest for road evidence priority rows."""

    exposed_rows = [
        row for row in rows if _int_value(row.get("canonical_exposure_rows", "")) > 0
    ]
    status_counts = _counts(row.get("priority_status", "") for row in rows)
    source_request_ids = sorted(
        {
            request_id
            for row in rows
            for request_id in str(row.get("needed_source_requests", "")).split("; ")
            if request_id
        }
    )
    return {
        "schema_version": 1,
        "result_scope": ROAD_EVIDENCE_PRIORITY_SCOPE,
        "claim_boundary": (
            "This packet prioritizes existing road evidence gaps by canonical "
            "route exposure. It does not create road_class_overrides.csv, "
            "does not certify source sufficiency, and does not close road, "
            "validation, graph-scale, or final-study gates."
        ),
        "row_count": len(rows),
        "exposed_highway_count": len(exposed_rows),
        "unexposed_highway_count": len(rows) - len(exposed_rows),
        "priority_status_counts": status_counts,
        "blocking_priority_count": sum(
            1
            for row in rows
            if str(row.get("priority_status", "")).startswith("blocked_")
        ),
        "needed_source_request_ids": source_request_ids,
        "publication_ready": False,
        "can_mark_complete": False,
        "inputs": {
            "road_evidence_review_packet": _display_path(road_evidence_review_path),
            "route_road_evidence_exposure": _display_path(route_exposure_path),
            "route_road_evidence_exposure_manifest": _display_path(
                route_exposure_manifest_path
            ),
            "road_source_readiness_packet": _display_path(road_source_readiness_path),
        },
        "outputs": {
            "csv": _display_path(output_path),
            "manifest": _display_path(manifest_path),
            "doc": _display_path(doc_path),
        },
        "review_items": [
            "collect or accept speed, capacity, and disruption evidence for exposed high-priority road classes first",
            "review connector assumptions separately from OSM road-class evidence",
            "use unexposed classes as lower-priority coverage unless graph-scale or route candidates change",
            "regenerate this packet after road-class overrides, route exposure, or graph-scale method changes",
        ],
        "remaining_blockers": [
            "reviewed road_class_overrides.csv is still absent",
            "capacity and disruption evidence still require source-backed or accepted assumption treatment",
            "connector assumptions still require route-plausibility review before route-level claims",
        ],
    }


def build_road_evidence_priority_markdown(
    manifest: Mapping[str, Any],
    *,
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Return Markdown for road evidence priority review."""

    lines = [
        "# Road Evidence Priority Packet",
        "",
        str(manifest.get("claim_boundary", ROAD_EVIDENCE_PRIORITY_SCOPE)),
        "",
        "## Verdict",
        "",
        f"- Publication ready: `{str(manifest.get('publication_ready', False)).lower()}`",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        f"- Priority rows: {manifest.get('row_count', 0)}",
        f"- Exposed highways: {manifest.get('exposed_highway_count', 0)}",
        f"- Blocking priority rows: {manifest.get('blocking_priority_count', 0)}",
        f"- Status counts: `{manifest.get('priority_status_counts', {})}`",
        "",
        "## Priority Rows",
        "",
        "| Highway | Status | Exposure Rows | Route Candidates | Time min | Max Time Share | Required Action |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            "| {highway} | {status} | {rows} | {candidates} | {time} | {share} | {action} |".format(
                highway=_cell(row.get("highway", "")),
                status=_cell(row.get("priority_status", "")),
                rows=_cell(row.get("canonical_exposure_rows", "")),
                candidates=_cell(row.get("exposed_route_candidate_count", "")),
                time=_cell(row.get("total_exposed_time_min", "")),
                share=_cell(row.get("max_route_time_share", "")),
                action=_cell(row.get("required_reviewer_action", "")),
            )
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This packet is road-evidence prioritization support only.",
            "- It does not create reviewed overrides, source acceptance, calibration, validation, graph-scale acceptance, or operational routing evidence.",
            "- It cannot create or replace `data/parameters/road_class_overrides.csv`.",
            "",
        ]
    )
    return "\n".join(lines)


def _priority_row(
    highway: str,
    road_row: Mapping[str, str],
    exposure: Mapping[str, Any],
    *,
    source_request_ids: set[str],
    route_exposure_artifacts: Sequence[str],
) -> dict[str, str]:
    exposure_count = int(exposure["row_count"])
    review_priority = str(road_row.get("review_priority", "") or "route_connector_review")
    speed_status = str(
        road_row.get("speed_evidence_status", "")
        or exposure.get("speed_evidence_status", "")
    )
    capacity_status = str(
        road_row.get("capacity_evidence_status", "")
        or exposure.get("capacity_evidence_status", "")
    )
    disruption_status = str(
        road_row.get("base_disruption_evidence_status", "")
        or exposure.get("base_disruption_evidence_status", "")
    )
    override_class = str(
        road_row.get("override_source_class", "")
        or exposure.get("override_source_class", "")
    )
    status = _priority_status(
        highway=highway,
        exposure_count=exposure_count,
        review_priority=review_priority,
    )
    return {
        "highway": highway,
        "review_priority": review_priority,
        "priority_status": status,
        "routeable_edge_count": str(road_row.get("routeable_edge_count", "0")),
        "routeable_length_km": str(road_row.get("routeable_length_km", "0")),
        "routeable_length_share": str(road_row.get("routeable_length_share", "0")),
        "canonical_exposure_rows": str(exposure_count),
        "exposed_route_count": str(len(exposure["route_ids"])),
        "exposed_route_candidate_count": str(len(exposure["route_candidates"])),
        "exposed_graph_variants": _join_sorted(exposure["graph_variants"]),
        "route_status_counts": _format_counts(exposure["route_status_counts"]),
        "total_exposed_distance_m": _format_float(exposure["distance_m"]),
        "total_exposed_time_min": _format_float(exposure["time_min"]),
        "max_route_time_share": _format_float(exposure["max_time_share"]),
        "speed_evidence_status": speed_status,
        "capacity_evidence_status": capacity_status,
        "base_disruption_evidence_status": disruption_status,
        "override_source_class": override_class,
        "needed_source_requests": _needed_source_requests(
            highway=highway,
            speed_status=speed_status,
            capacity_status=capacity_status,
            disruption_status=disruption_status,
            override_source_class=override_class,
            exposure_count=exposure_count,
            source_request_ids=source_request_ids,
        ),
        "candidate_artifacts": _artifact_list(
            road_row.get("candidate_artifacts", ""),
            exposure.get("candidate_artifacts", ""),
            *route_exposure_artifacts,
        ),
        "required_reviewer_action": _required_action(
            highway=highway,
            exposure_count=exposure_count,
            status=status,
        ),
        "publication_use_status": "priority_review_support_only_not_road_acceptance",
        "can_support_road_evidence_gate": "false",
        "claim_boundary": ROAD_EVIDENCE_PRIORITY_SCOPE,
    }


def _aggregate_exposure(rows: Sequence[Mapping[str, str]]) -> dict[str, dict[str, Any]]:
    aggregates = defaultdict(_empty_exposure)
    for row in rows:
        highway = str(row.get("highway", "")).strip()
        if not highway:
            continue
        aggregate = aggregates[highway]
        aggregate["row_count"] += 1
        aggregate["route_ids"].add(str(row.get("route_check_id", "")))
        aggregate["route_candidates"].add(
            (
                str(row.get("graph_variant", "")),
                str(row.get("route_check_id", "")),
                str(row.get("route_rank", "")),
            )
        )
        aggregate["graph_variants"].add(str(row.get("graph_variant", "")))
        aggregate["route_status_counts"][str(row.get("route_status", ""))] += 1
        aggregate["distance_m"] += _float_value(row.get("distance_m", ""))
        aggregate["time_min"] += _float_value(row.get("time_min", ""))
        aggregate["max_time_share"] = max(
            aggregate["max_time_share"],
            _float_value(row.get("time_share", "")),
        )
        for key in (
            "speed_evidence_status",
            "capacity_evidence_status",
            "base_disruption_evidence_status",
            "override_source_class",
            "candidate_artifacts",
        ):
            if not aggregate.get(key) and row.get(key):
                aggregate[key] = str(row.get(key, ""))
    return dict(aggregates)


def _empty_exposure() -> dict[str, Any]:
    return {
        "row_count": 0,
        "route_ids": set(),
        "route_candidates": set(),
        "graph_variants": set(),
        "route_status_counts": Counter(),
        "distance_m": 0.0,
        "time_min": 0.0,
        "max_time_share": 0.0,
        "speed_evidence_status": "",
        "capacity_evidence_status": "",
        "base_disruption_evidence_status": "",
        "override_source_class": "",
        "candidate_artifacts": "",
    }


def _priority_status(
    *,
    highway: str,
    exposure_count: int,
    review_priority: str,
) -> str:
    if highway == "connector" and exposure_count:
        return "blocked_exposed_connector_assumption"
    if not exposure_count:
        return "queued_no_current_canonical_route_exposure"
    if review_priority == "high":
        return "blocked_exposed_high_priority_road_evidence_gap"
    return "needs_review_exposed_medium_priority_road_evidence_gap"


def _needed_source_requests(
    *,
    highway: str,
    speed_status: str,
    capacity_status: str,
    disruption_status: str,
    override_source_class: str,
    exposure_count: int,
    source_request_ids: set[str],
) -> str:
    requests: list[str] = []
    if highway == "connector":
        requests.append("route_plausibility_connector_review")
        if exposure_count:
            requests.append("road_background_traffic_benchmark_request")
        return _join_sorted(requests)
    if "missing" in speed_status or "sparse" in speed_status:
        requests.append("road_speed_limit_source_request")
    if "missing" in capacity_status or "assumption" in capacity_status:
        requests.append("road_capacity_lane_count_source_request")
    if "missing" in disruption_status or "assumption" in disruption_status:
        requests.append("road_disruption_probability_source_request")
    if exposure_count:
        requests.append("road_background_traffic_benchmark_request")
    if override_source_class and override_source_class != "source-backed":
        requests.append("reviewed_road_class_override_application_request")
    known_or_local = [
        request
        for request in requests
        if request in source_request_ids or request == "route_plausibility_connector_review"
    ]
    return _join_sorted(known_or_local)


def _required_action(*, highway: str, exposure_count: int, status: str) -> str:
    if highway == "connector":
        return (
            "review connector snapping distances, connector travel times, capacity "
            "assumptions, and zero-failure treatment before route-level claims"
        )
    if not exposure_count:
        return (
            "keep this class in the road override review backlog unless graph-scale "
            "or route-candidate changes expose it"
        )
    if status.startswith("blocked_"):
        return (
            "prioritize reviewed or explicitly accepted speed, capacity, and "
            "disruption values for this exposed road class"
        )
    return (
        "review after exposed high-priority classes, or sooner if graph-scale "
        "selection makes this class claim-relevant"
    )


def _priority_sort_key(row: Mapping[str, str]) -> tuple[int, float, str]:
    status_order = {
        "blocked_exposed_high_priority_road_evidence_gap": 0,
        "blocked_exposed_connector_assumption": 1,
        "needs_review_exposed_medium_priority_road_evidence_gap": 2,
        "queued_no_current_canonical_route_exposure": 3,
    }
    return (
        status_order.get(str(row.get("priority_status", "")), 99),
        -_float_value(row.get("total_exposed_time_min", "")),
        str(row.get("highway", "")),
    )


def _read_csv_rows(path: str | Path) -> list[dict[str, str]]:
    filepath = Path(path)
    with filepath.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _counts(values: Iterable[Any]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for value in values:
        key = str(value).strip() or "blank"
        counts[key] += 1
    return dict(sorted(counts.items()))


def _format_counts(counter: Counter[str]) -> str:
    return "; ".join(f"{key}={value}" for key, value in sorted(counter.items()) if key)


def _join_sorted(values: Iterable[Any]) -> str:
    return "; ".join(sorted({str(value).strip() for value in values if str(value).strip()}))


def _artifact_list(*values: Any) -> str:
    artifacts: list[str] = []
    seen: set[str] = set()
    for value in values:
        for artifact in str(value).split(";"):
            clean = artifact.strip()
            if clean and clean not in seen:
                seen.add(clean)
                artifacts.append(clean)
    return "; ".join(artifacts)


def _float_value(value: Any) -> float:
    try:
        text = str(value).strip()
        return float(text) if text else 0.0
    except (TypeError, ValueError):
        return 0.0


def _int_value(value: Any) -> int:
    try:
        text = str(value).strip()
        return int(float(text)) if text else 0
    except (TypeError, ValueError):
        return 0


def _format_float(value: Any) -> str:
    return f"{_float_value(value):.6f}".rstrip("0").rstrip(".")


def _display_path(path: str | Path) -> str:
    filepath = Path(path)
    try:
        return filepath.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return filepath.as_posix()


def _cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


__all__ = [
    "DEFAULT_ROAD_EVIDENCE_PRIORITY_DOC_PATH",
    "DEFAULT_ROAD_EVIDENCE_PRIORITY_MANIFEST_PATH",
    "DEFAULT_ROAD_EVIDENCE_PRIORITY_PACKET_PATH",
    "ROAD_EVIDENCE_PRIORITY_COLUMNS",
    "ROAD_EVIDENCE_PRIORITY_SCOPE",
    "build_road_evidence_priority_manifest",
    "build_road_evidence_priority_markdown",
    "build_road_evidence_priority_rows",
    "write_road_evidence_priority_packet",
]
