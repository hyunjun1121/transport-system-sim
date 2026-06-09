"""Load road-class speed, capacity, and disruption override tables."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from src.realworld.attributes import HIGHWAY_DEFAULTS, RoadClassDefaults
from src.realworld.parameters import ALLOWED_SOURCE_CLASSES


REQUIRED_COLUMNS: tuple[str, ...] = (
    "highway",
    "speed_kph",
    "capacity_veh_per_hr",
    "base_p_fail",
    "source_class",
    "source_name",
    "source_url_or_citation",
    "notes",
)

OPTIONAL_FIELD_SOURCE_COLUMNS: tuple[str, ...] = (
    "speed_source_class",
    "speed_source_name",
    "speed_source_url_or_citation",
    "capacity_source_class",
    "capacity_source_name",
    "capacity_source_url_or_citation",
    "base_p_fail_source_class",
    "base_p_fail_source_name",
    "base_p_fail_source_url_or_citation",
)


@dataclass(frozen=True)
class RoadClassOverride:
    """One source-backed or accepted road-class override row."""

    highway: str
    speed_kph: float
    capacity_veh_per_hr: float
    base_p_fail: float
    source_class: str
    source_name: str
    source_url_or_citation: str
    notes: str
    speed_source_class: str
    speed_source_name: str
    speed_source_url_or_citation: str
    capacity_source_class: str
    capacity_source_name: str
    capacity_source_url_or_citation: str
    base_p_fail_source_class: str
    base_p_fail_source_name: str
    base_p_fail_source_url_or_citation: str

    @property
    def defaults(self) -> RoadClassDefaults:
        """Return mapper defaults represented by this row."""

        return RoadClassDefaults(
            speed_kph=self.speed_kph,
            capacity=self.capacity_veh_per_hr,
            base_p_fail=self.base_p_fail,
        )


def load_road_class_overrides(path: str | Path) -> list[RoadClassOverride]:
    """Load and validate road-class override rows."""

    override_path = Path(path)
    with override_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        _validate_columns(reader.fieldnames, override_path)
        overrides: list[RoadClassOverride] = []
        for row in reader:
            if None in row:
                raise ValueError(f"{override_path}:{reader.line_num} has too many columns")
            if not any(_clean(value) for value in row.values()):
                continue
            overrides.append(_override_from_row(row, override_path, reader.line_num))
    validate_road_class_overrides(overrides, table_name=str(override_path))
    return overrides


def validate_road_class_overrides(
    overrides: Sequence[RoadClassOverride],
    *,
    table_name: str = "road class overrides",
) -> None:
    """Validate table-level road-class override invariants."""

    if not overrides:
        raise ValueError(f"{table_name} must contain at least one override row")
    seen: set[str] = set()
    duplicates: set[str] = set()
    for override in overrides:
        if override.highway in seen:
            duplicates.add(override.highway)
        seen.add(override.highway)
    if duplicates:
        raise ValueError(
            f"{table_name} has duplicate highway rows: {', '.join(sorted(duplicates))}"
        )


def build_highway_defaults_with_overrides(
    overrides: Sequence[RoadClassOverride],
    *,
    base_defaults: Mapping[str, RoadClassDefaults] = HIGHWAY_DEFAULTS,
) -> dict[str, RoadClassDefaults]:
    """Return a copy of base road-class defaults with overrides applied."""

    merged = dict(base_defaults)
    for override in overrides:
        merged[override.highway] = override.defaults
    return merged


def build_road_class_override_metadata(
    overrides: Sequence[RoadClassOverride],
) -> dict[str, dict[str, Any]]:
    """Return source metadata keyed by highway class for downstream traceability."""

    validate_road_class_overrides(overrides)
    return {
        override.highway: {
            "highway": override.highway,
            "speed_kph": override.speed_kph,
            "capacity_veh_per_hr": override.capacity_veh_per_hr,
            "base_p_fail": override.base_p_fail,
            "source_class": override.source_class,
            "source_name": override.source_name,
            "source_url_or_citation": override.source_url_or_citation,
            "field_sources": {
                "speed_kph": {
                    "source_class": override.speed_source_class,
                    "source_name": override.speed_source_name,
                    "source_url_or_citation": override.speed_source_url_or_citation,
                },
                "capacity_veh_per_hr": {
                    "source_class": override.capacity_source_class,
                    "source_name": override.capacity_source_name,
                    "source_url_or_citation": override.capacity_source_url_or_citation,
                },
                "base_p_fail": {
                    "source_class": override.base_p_fail_source_class,
                    "source_name": override.base_p_fail_source_name,
                    "source_url_or_citation": override.base_p_fail_source_url_or_citation,
                },
            },
            "notes": override.notes,
        }
        for override in overrides
    }


def _validate_columns(fieldnames: Sequence[str] | None, path: Path) -> None:
    if not fieldnames:
        raise ValueError(f"{path} must have a CSV header")
    missing = [column for column in REQUIRED_COLUMNS if column not in fieldnames]
    if missing:
        raise ValueError(f"{path} missing required columns: {', '.join(missing)}")


def _override_from_row(
    row: Mapping[str, str | None],
    path: Path,
    line_num: int,
) -> RoadClassOverride:
    values = {column: _clean(row.get(column)) for column in REQUIRED_COLUMNS}
    for column, value in values.items():
        if not value:
            raise ValueError(f"{path}:{line_num} field {column!r} must be non-empty")

    highway = values["highway"].lower()
    if highway not in HIGHWAY_DEFAULTS:
        raise ValueError(f"{path}:{line_num} unknown highway class {highway!r}")
    source_class = values["source_class"].lower()
    if source_class not in ALLOWED_SOURCE_CLASSES:
        raise ValueError(f"{path}:{line_num} invalid source_class {source_class!r}")
    field_sources = _field_sources_from_row(row, source_class, values, path, line_num)

    return RoadClassOverride(
        highway=highway,
        speed_kph=_positive_number(values["speed_kph"], path, line_num),
        capacity_veh_per_hr=_positive_number(
            values["capacity_veh_per_hr"],
            path,
            line_num,
        ),
        base_p_fail=_probability(values["base_p_fail"], path, line_num),
        source_class=source_class,
        source_name=values["source_name"],
        source_url_or_citation=values["source_url_or_citation"],
        notes=values["notes"],
        **field_sources,
    )


def _field_sources_from_row(
    row: Mapping[str, str | None],
    source_class: str,
    values: Mapping[str, str],
    path: Path,
    line_num: int,
) -> dict[str, str]:
    field_sources: dict[str, str] = {}
    for prefix in ("speed", "capacity", "base_p_fail"):
        class_column = f"{prefix}_source_class"
        name_column = f"{prefix}_source_name"
        citation_column = f"{prefix}_source_url_or_citation"
        class_value = _clean(row.get(class_column)).lower()
        name_value = _clean(row.get(name_column))
        citation_value = _clean(row.get(citation_column))

        present = bool(class_value or name_value or citation_value)
        if not present:
            field_sources[class_column] = source_class
            field_sources[name_column] = values["source_name"]
            field_sources[citation_column] = values["source_url_or_citation"]
            continue

        if not class_value:
            raise ValueError(f"{path}:{line_num} field {class_column!r} must be non-empty")
        if class_value not in ALLOWED_SOURCE_CLASSES:
            raise ValueError(f"{path}:{line_num} invalid {class_column} {class_value!r}")
        if not name_value:
            raise ValueError(f"{path}:{line_num} field {name_column!r} must be non-empty")
        if not citation_value:
            raise ValueError(f"{path}:{line_num} field {citation_column!r} must be non-empty")
        field_sources[class_column] = class_value
        field_sources[name_column] = name_value
        field_sources[citation_column] = citation_value
    return field_sources


def _positive_number(value: str, path: Path, line_num: int) -> float:
    try:
        parsed = float(value)
    except ValueError as exc:
        raise ValueError(f"{path}:{line_num} expected numeric value {value!r}") from exc
    if parsed <= 0.0:
        raise ValueError(f"{path}:{line_num} expected positive value {value!r}")
    return parsed


def _probability(value: str, path: Path, line_num: int) -> float:
    try:
        parsed = float(value)
    except ValueError as exc:
        raise ValueError(f"{path}:{line_num} expected probability {value!r}") from exc
    if not 0.0 <= parsed <= 1.0:
        raise ValueError(f"{path}:{line_num} expected 0 <= p <= 1, got {value!r}")
    return parsed


def _clean(value: object) -> str:
    return "" if value is None else str(value).strip()


__all__ = [
    "REQUIRED_COLUMNS",
    "OPTIONAL_FIELD_SOURCE_COLUMNS",
    "RoadClassOverride",
    "build_highway_defaults_with_overrides",
    "build_road_class_override_metadata",
    "load_road_class_overrides",
    "validate_road_class_overrides",
]
