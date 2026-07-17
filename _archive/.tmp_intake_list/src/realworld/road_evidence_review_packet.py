"""Road-input evidence review-packet generation.

This module consolidates cached road diagnostics, sparse OSM speed evidence,
lane-count capacity evidence, and draft road-class override rows into one
review worksheet. The packet supports road-input evidence review; it is not a
calibration table, accepted override table, or operational road validation.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from src.realworld.road_capacity_evidence import (
    build_cached_road_capacity_evidence_rows,
)
from src.realworld.road_evidence import DEFAULT_ROAD_GRAPH_PATH
from src.realworld.road_evidence_diagnostics import (
    audit_cached_road_evidence_diagnostics,
)
from src.realworld.road_override_audit import (
    DEFAULT_ROAD_CLASS_OVERRIDE_DRAFT_PATH,
    STRONG_SOURCE_CLASSES,
)
from src.realworld.road_overrides import RoadClassOverride, load_road_class_overrides
from src.realworld.road_speed_evidence import build_cached_road_speed_evidence_rows


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ROAD_EVIDENCE_REVIEW_PACKET_PATH = (
    PROJECT_ROOT / "data" / "parameters" / "road_evidence_review_packet.csv"
)
DEFAULT_ROAD_EVIDENCE_REVIEW_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "parameters" / "road_evidence_review_manifest.json"
)
ROAD_EVIDENCE_REVIEW_PACKET_SCOPE = (
    "Road-input evidence review packet; not accepted road calibration, "
    "road-class override evidence, traffic assignment validation, or "
    "operational routing evidence."
)
ROAD_EVIDENCE_REVIEW_COLUMNS: tuple[str, ...] = (
    "highway",
    "review_priority",
    "routeable_edge_count",
    "routeable_length_km",
    "routeable_length_share",
    "speed_evidence_status",
    "maxspeed_observed_count",
    "maxspeed_observed_rate",
    "observed_speed_length_share",
    "mapper_default_speed_kph",
    "candidate_speed_kph",
    "speed_source_class",
    "capacity_evidence_status",
    "lanes_observed_count",
    "lanes_observed_rate",
    "mapper_default_capacity_veh_per_hr",
    "candidate_capacity_veh_per_hr",
    "capacity_source_class",
    "base_disruption_evidence_status",
    "base_disruption_explicit_rate",
    "current_base_p_fail",
    "base_disruption_source_class",
    "override_source_class",
    "weak_for_final_claim",
    "recommended_upgrade",
    "candidate_artifacts",
    "publication_use_status",
    "claim_boundary",
    "notes",
)


def build_road_evidence_review_rows(
    *,
    input_graph: str | Path = DEFAULT_ROAD_GRAPH_PATH,
    draft_override_path: str | Path = DEFAULT_ROAD_CLASS_OVERRIDE_DRAFT_PATH,
) -> list[dict[str, str]]:
    """Return road-class review rows for the cached pilot graph."""

    diagnostics = audit_cached_road_evidence_diagnostics(input_graph)
    speed_rows = _rows_by_highway(build_cached_road_speed_evidence_rows(input_graph))
    capacity_rows = _rows_by_highway(
        build_cached_road_capacity_evidence_rows(input_graph)
    )
    overrides = _overrides_by_highway(draft_override_path)

    rows: list[dict[str, str]] = []
    for diagnostic in diagnostics.get("road_class_rows", []):
        if not isinstance(diagnostic, Mapping):
            continue
        highway = str(diagnostic.get("highway", "")).strip()
        if not highway:
            continue
        if int(str(diagnostic.get("routeable_edge_count", "0") or "0")) <= 0:
            continue
        speed = speed_rows.get(highway, {})
        capacity = capacity_rows.get(highway, {})
        override = overrides.get(highway)
        rows.append(_review_row(diagnostic, speed, capacity, override))

    rows.sort(
        key=lambda row: (
            _priority_rank(row["review_priority"]),
            -_float(row["routeable_length_share"]),
            row["highway"],
        )
    )
    return rows


def write_road_evidence_review_packet(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_ROAD_EVIDENCE_REVIEW_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_ROAD_EVIDENCE_REVIEW_MANIFEST_PATH,
    input_graph: str | Path = DEFAULT_ROAD_GRAPH_PATH,
    draft_override_path: str | Path = DEFAULT_ROAD_CLASS_OVERRIDE_DRAFT_PATH,
) -> dict[str, Any]:
    """Write road-evidence review rows and a conservative manifest."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=ROAD_EVIDENCE_REVIEW_COLUMNS,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)

    weak_rows = [
        row
        for row in rows
        if str(row.get("weak_for_final_claim", "")).lower() == "true"
    ]
    value = {
        "schema_version": 1,
        "result_scope": ROAD_EVIDENCE_REVIEW_PACKET_SCOPE,
        "input_graph": _display_path(input_graph),
        "draft_override_path": _display_path(draft_override_path),
        "outputs": {
            "road_evidence_review_packet": _display_path(output),
            "manifest": _display_path(manifest),
        },
        "row_count": len(rows),
        "weak_for_final_claim_count": len(weak_rows),
        "review_priority_counts": _counts(row["review_priority"] for row in rows),
        "speed_status_counts": _counts(
            row["speed_evidence_status"] for row in rows
        ),
        "capacity_status_counts": _counts(
            row["capacity_evidence_status"] for row in rows
        ),
        "base_disruption_status_counts": _counts(
            row["base_disruption_evidence_status"] for row in rows
        ),
        "publication_ready": False,
        "claim_boundary": (
            "This packet organizes road-input evidence review by road class. "
            "It does not create accepted road-class overrides, calibrated road "
            "capacity, disruption probabilities, traffic assignment, or final "
            "publication readiness."
        ),
        "review_items": [
            "replace high-priority weak road classes with source-backed speed, capacity, and base-disruption evidence",
            "move accepted values into data/parameters/road_class_overrides.csv only after review",
            "apply reviewed overrides in the pilot graph adapter before making road-calibration claims",
            "rerun road, publication-readiness, and final-study-readiness audits after road evidence changes",
        ],
    }
    with manifest.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return value


def _review_row(
    diagnostic: Mapping[str, object],
    speed: Mapping[str, str],
    capacity: Mapping[str, str],
    override: RoadClassOverride | None,
) -> dict[str, str]:
    speed_status = _speed_status(speed)
    capacity_status = _capacity_status(capacity)
    disruption_status = _disruption_status(diagnostic, override)
    override_source_class = "" if override is None else override.source_class
    weak = (
        speed_status != "reviewed_or_high_coverage"
        or capacity_status != "reviewed_or_high_coverage"
        or disruption_status != "reviewed_or_explicit"
        or override_source_class not in STRONG_SOURCE_CLASSES
    )

    return {
        "highway": str(diagnostic.get("highway", "")),
        "review_priority": str(diagnostic.get("review_priority", "low")),
        "routeable_edge_count": str(diagnostic.get("routeable_edge_count", "0")),
        "routeable_length_km": _text(diagnostic.get("routeable_length_km")),
        "routeable_length_share": _text(diagnostic.get("routeable_length_share")),
        "speed_evidence_status": speed_status,
        "maxspeed_observed_count": str(speed.get("maxspeed_observed_count", "0")),
        "maxspeed_observed_rate": str(speed.get("maxspeed_observed_rate", "0")),
        "observed_speed_length_share": str(speed.get("observed_length_share", "0")),
        "mapper_default_speed_kph": str(speed.get("mapper_default_speed_kph", "")),
        "candidate_speed_kph": str(speed.get("candidate_speed_kph", "")),
        "speed_source_class": str(speed.get("candidate_source_class", "")),
        "capacity_evidence_status": capacity_status,
        "lanes_observed_count": str(capacity.get("lanes_observed_count", "0")),
        "lanes_observed_rate": str(capacity.get("lanes_observed_rate", "0")),
        "mapper_default_capacity_veh_per_hr": str(
            capacity.get("mapper_default_capacity_veh_per_hr", "")
        ),
        "candidate_capacity_veh_per_hr": str(
            capacity.get("candidate_capacity_veh_per_hr", "")
        ),
        "capacity_source_class": str(capacity.get("candidate_source_class", "")),
        "base_disruption_evidence_status": disruption_status,
        "base_disruption_explicit_rate": _text(
            diagnostic.get("base_disruption_explicit_rate")
        ),
        "current_base_p_fail": "" if override is None else _text(override.base_p_fail),
        "base_disruption_source_class": override_source_class,
        "override_source_class": override_source_class,
        "weak_for_final_claim": str(weak).lower(),
        "recommended_upgrade": _recommended_upgrade(speed_status, capacity_status, disruption_status),
        "candidate_artifacts": (
            "data/parameters/road_speed_evidence_candidates.csv; "
            "data/parameters/road_capacity_evidence_candidates.csv; "
            "data/parameters/road_class_overrides_draft.csv"
        ),
        "publication_use_status": "blocked_until_reviewed_override_and_application",
        "claim_boundary": ROAD_EVIDENCE_REVIEW_PACKET_SCOPE,
        "notes": _notes(speed_status, capacity_status, disruption_status),
    }


def _speed_status(row: Mapping[str, str]) -> str:
    if _float(row.get("maxspeed_observed_rate", "0")) >= 0.95:
        return "reviewed_or_high_coverage"
    if int(str(row.get("maxspeed_observed_count", "0") or "0")) > 0:
        return "sparse_public_maxspeed_tags"
    return "missing_public_speed_evidence"


def _capacity_status(row: Mapping[str, str]) -> str:
    if _float(row.get("lanes_observed_rate", "0")) >= 0.95:
        return "reviewed_or_high_coverage"
    if int(str(row.get("lanes_observed_count", "0") or "0")) > 0:
        return "sparse_lane_tags_plus_proxy"
    return "missing_lane_or_capacity_evidence"


def _disruption_status(
    diagnostic: Mapping[str, object],
    override: RoadClassOverride | None,
) -> str:
    if _float(diagnostic.get("base_disruption_explicit_rate")) >= 0.95:
        return "reviewed_or_explicit"
    if override is not None and override.source_class in STRONG_SOURCE_CLASSES:
        return "source_backed_override"
    return "missing_disruption_probability_evidence"


def _recommended_upgrade(
    speed_status: str,
    capacity_status: str,
    disruption_status: str,
) -> str:
    upgrades: list[str] = []
    if speed_status != "reviewed_or_high_coverage":
        upgrades.append("speed: review public speed limits, OSM maxspeed coverage, or routing benchmark")
    if capacity_status != "reviewed_or_high_coverage":
        upgrades.append("capacity: add traffic counts, agency class capacities, or reviewed per-lane assumptions")
    if disruption_status != "reviewed_or_explicit":
        upgrades.append("disruption: add hazard, incident, scenario, or reviewed sensitivity evidence")
    return "; ".join(upgrades)


def _notes(
    speed_status: str,
    capacity_status: str,
    disruption_status: str,
) -> str:
    statuses = [speed_status, capacity_status, disruption_status]
    if all(status.startswith("reviewed") for status in statuses):
        return "Current road-class evidence is structurally strong under packet rules."
    return (
        "Use this row to prepare reviewed road_class_overrides.csv values; "
        "do not cite it as accepted calibration."
    )


def _rows_by_highway(rows: Sequence[Mapping[str, str]]) -> dict[str, Mapping[str, str]]:
    return {str(row.get("highway", "")).strip(): row for row in rows}


def _overrides_by_highway(path: str | Path) -> dict[str, RoadClassOverride]:
    override_path = Path(path)
    if not override_path.exists():
        return {}
    return {override.highway: override for override in load_road_class_overrides(override_path)}


def _priority_rank(priority: str) -> int:
    return {"high": 0, "medium": 1, "low": 2}.get(priority, 3)


def _float(value: object) -> float:
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return 0.0


def _text(value: object) -> str:
    if value is None:
        return ""
    return f"{value:.6f}".rstrip("0").rstrip(".") if isinstance(value, float) else str(value)


def _counts(values: Sequence[str] | Any) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value)
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _display_path(path: str | Path) -> str:
    filepath = Path(path)
    try:
        return filepath.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return filepath.as_posix()


__all__ = [
    "DEFAULT_ROAD_EVIDENCE_REVIEW_MANIFEST_PATH",
    "DEFAULT_ROAD_EVIDENCE_REVIEW_PACKET_PATH",
    "ROAD_EVIDENCE_REVIEW_COLUMNS",
    "ROAD_EVIDENCE_REVIEW_PACKET_SCOPE",
    "build_road_evidence_review_rows",
    "write_road_evidence_review_packet",
]
