"""Build draft road-class override tables from road evidence diagnostics."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from src.realworld.attributes import HIGHWAY_DEFAULTS
from src.realworld.road_overrides import OPTIONAL_FIELD_SOURCE_COLUMNS, REQUIRED_COLUMNS


TEMPLATE_EXTRA_COLUMNS: tuple[str, ...] = (
    "review_priority",
    "routeable_edge_count",
    "routeable_length_km",
    "routeable_length_share",
    "maxspeed_parseable_rate",
    "capacity_explicit_rate",
    "base_disruption_explicit_rate",
)

TEMPLATE_COLUMNS: tuple[str, ...] = (
    REQUIRED_COLUMNS + OPTIONAL_FIELD_SOURCE_COLUMNS + TEMPLATE_EXTRA_COLUMNS
)


def build_road_class_override_template_rows(
    diagnostics: Mapping[str, Any],
    *,
    include_low_priority: bool = False,
    top_n: int | None = None,
    observed_speed_classes: set[str] | None = None,
) -> list[dict[str, str]]:
    """Return draft override rows for routeable highway classes needing review.

    The generated values intentionally mirror current mapper defaults and use
    ``expert assumption`` as the source class. They are review scaffolds, not
    publication-ready evidence.

    When *observed_speed_classes* is provided, those highway classes are
    marked ``public-data-derived`` for the speed field source, reflecting
    observed OSM maxspeed tags on routeable edges.
    """

    rows = _diagnostic_rows(diagnostics)
    candidates: list[Mapping[str, Any]] = []
    for row in rows:
        highway = str(row.get("highway", "")).strip().lower()
        if not highway or highway not in HIGHWAY_DEFAULTS:
            continue
        if _int_value(row.get("routeable_edge_count")) <= 0:
            continue
        priority = str(row.get("review_priority", "")).strip().lower()
        if not include_low_priority and priority not in {"high", "medium"}:
            continue
        candidates.append(row)

    candidates.sort(
        key=lambda row: (
            _priority_order(str(row.get("review_priority", ""))),
            -_float_value(row.get("routeable_length_share")),
            -_int_value(row.get("routeable_edge_count")),
            str(row.get("highway", "")),
        )
    )
    if top_n is not None:
        if top_n <= 0:
            raise ValueError("top_n must be positive when provided")
        candidates = candidates[:top_n]

    resolved_observed = observed_speed_classes or set()
    return [
        _template_row(candidate, resolved_observed) for candidate in candidates
    ]


def write_road_class_override_template(
    path: str | Path,
    rows: Sequence[Mapping[str, str]],
) -> None:
    """Write draft road-class override rows as a CSV table."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=TEMPLATE_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _diagnostic_rows(diagnostics: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    value = diagnostics.get("road_class_rows", [])
    if not isinstance(value, list):
        raise ValueError("diagnostics must contain a road_class_rows list")
    rows: list[Mapping[str, Any]] = []
    for row in value:
        if not isinstance(row, Mapping):
            raise ValueError("each road_class_rows item must be a mapping")
        rows.append(row)
    return rows


def _template_row(
    row: Mapping[str, Any],
    observed_speed_classes: set[str],
) -> dict[str, str]:
    highway = str(row["highway"]).strip().lower()
    defaults = HIGHWAY_DEFAULTS[highway]
    if highway in observed_speed_classes:
        speed_source_class = "public-data-derived"
        speed_source_name = (
            "cached OSM maxspeed tags; see road_speed_evidence_candidates.csv"
        )
        speed_source_citation = (
            "data/parameters/road_speed_evidence_candidates.csv"
        )
    else:
        speed_source_class = "expert assumption"
        speed_source_name = "draft mapper speed default pending road-evidence review"
        speed_source_citation = "src/realworld/attributes.py"
    return {
        "highway": highway,
        "speed_kph": _format_number(defaults.speed_kph),
        "capacity_veh_per_hr": _format_number(defaults.capacity),
        "base_p_fail": _format_number(defaults.base_p_fail),
        "source_class": "expert assumption",
        "source_name": "draft mapper default pending road-evidence review",
        "source_url_or_citation": "src/realworld/attributes.py",
        "speed_source_class": speed_source_class,
        "speed_source_name": speed_source_name,
        "speed_source_url_or_citation": speed_source_citation,
        "capacity_source_class": "expert assumption",
        "capacity_source_name": "draft mapper capacity default pending road-evidence review",
        "capacity_source_url_or_citation": "src/realworld/attributes.py",
        "base_p_fail_source_class": "sensitivity-only",
        "base_p_fail_source_name": "draft mapper base-disruption scenario proxy",
        "base_p_fail_source_url_or_citation": "src/realworld/attributes.py",
        "notes": (
            "DRAFT ONLY: replace with reviewed speed, capacity, and "
            "base-disruption evidence before using in final claims."
        ),
        "review_priority": str(row.get("review_priority", "")),
        "routeable_edge_count": str(_int_value(row.get("routeable_edge_count"))),
        "routeable_length_km": _format_number(row.get("routeable_length_km")),
        "routeable_length_share": _format_number(row.get("routeable_length_share")),
        "maxspeed_parseable_rate": _format_number(row.get("maxspeed_parseable_rate")),
        "capacity_explicit_rate": _format_number(row.get("capacity_explicit_rate")),
        "base_disruption_explicit_rate": _format_number(
            row.get("base_disruption_explicit_rate")
        ),
    }


def _priority_order(priority: str) -> int:
    return {"high": 0, "medium": 1, "low": 2}.get(priority.lower(), 3)


def _int_value(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _float_value(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _format_number(value: Any) -> str:
    parsed = _float_value(value)
    text = f"{parsed:.6f}".rstrip("0").rstrip(".")
    return text or "0"


__all__ = [
    "TEMPLATE_COLUMNS",
    "TEMPLATE_EXTRA_COLUMNS",
    "build_road_class_override_template_rows",
    "write_road_class_override_template",
]
