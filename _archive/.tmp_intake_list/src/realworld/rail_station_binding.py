"""Validate rail-point bindings to public station identifiers.

The simulator uses abstract rail points such as ``S`` and ``R``. This module
keeps the evidence for mapping those points to station identifiers separate
from rail headway and travel-time evidence. A non-official station-area context
row is useful documentation, but it must not unlock publication-grade claims.
"""

from __future__ import annotations

import csv
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RAIL_STATION_BINDING_PATH = (
    PROJECT_ROOT / "data" / "parameters" / "rail_station_bindings.csv"
)

REQUIRED_COLUMNS: tuple[str, ...] = (
    "binding_id",
    "region_id",
    "point_id",
    "station_name",
    "station_id",
    "station_code",
    "source_name",
    "source_url_or_citation",
    "source_accessed_date",
    "source_status",
    "claim_scope",
    "notes",
)

ALLOWED_SOURCE_STATUSES: frozenset[str] = frozenset(
    {
        "official_station_code_bound",
        "public_station_name_context",
        "documented_assumption_proxy",
    }
)
OFFICIAL_SOURCE_STATUS = "official_station_code_bound"
NON_OFFICIAL_SOURCE_STATUSES: frozenset[str] = frozenset(
    ALLOWED_SOURCE_STATUSES - {OFFICIAL_SOURCE_STATUS}
)
PLACEHOLDER_VALUES: frozenset[str] = frozenset(
    {"", "-", "na", "n/a", "none", "null", "pending", "tbd", "unknown"}
)


@dataclass(frozen=True)
class RailStationBinding:
    """One row mapping a simulator rail point to station context."""

    binding_id: str
    region_id: str
    point_id: str
    station_name: str
    station_id: str
    station_code: str
    source_name: str
    source_url_or_citation: str
    source_accessed_date: str
    source_status: str
    claim_scope: str
    notes: str

    @property
    def is_official(self) -> bool:
        """Return whether this row binds to an official station identifier."""

        return self.source_status == OFFICIAL_SOURCE_STATUS


def load_rail_station_bindings(
    path: str | Path = DEFAULT_RAIL_STATION_BINDING_PATH,
) -> list[RailStationBinding]:
    """Load and validate station-binding evidence rows."""

    binding_path = Path(path)
    with binding_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        _validate_columns(reader.fieldnames, binding_path)
        records: list[RailStationBinding] = []
        for row in reader:
            if None in row:
                raise ValueError(f"{binding_path}:{reader.line_num} has too many columns")
            if not any(_clean(value) for value in row.values()):
                continue
            record = _record_from_row(row, binding_path, reader.line_num)
            _validate_record(record, binding_path, reader.line_num)
            records.append(record)
    validate_rail_station_bindings(records, table_name=str(binding_path))
    return records


def validate_rail_station_bindings(
    records: Sequence[RailStationBinding],
    *,
    table_name: str = "rail station bindings",
) -> None:
    """Validate table-level station-binding invariants."""

    if not records:
        raise ValueError(f"{table_name} must contain at least one row")
    duplicate_ids = _duplicates(record.binding_id for record in records)
    if duplicate_ids:
        raise ValueError(
            f"{table_name} has duplicate binding_id rows: "
            f"{', '.join(sorted(duplicate_ids))}"
        )


def write_rail_station_bindings(
    records: Iterable[RailStationBinding],
    path: str | Path,
) -> Path:
    """Write station-binding records using the repository schema."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REQUIRED_COLUMNS)
        writer.writeheader()
        for record in records:
            writer.writerow(_record_to_row(record))
    return output_path


def summarize_rail_station_bindings(
    records: Sequence[RailStationBinding],
    *,
    required_points: Sequence[str] = ("S", "R"),
) -> dict[str, object]:
    """Return conservative station-binding readiness for required rail points."""

    required = tuple(dict.fromkeys(_clean(point) for point in required_points if _clean(point)))
    official_points = {
        record.point_id for record in records if record.is_official and record.point_id in required
    }
    present_points = {record.point_id for record in records if record.point_id in required}
    missing_rows = sorted(set(required) - present_points)
    unofficial = sorted(present_points - official_points)

    status_counts = Counter(record.source_status for record in records)
    return {
        "row_count": len(records),
        "required_points": list(required),
        "source_status_counts": dict(sorted(status_counts.items())),
        "official_required_points": sorted(official_points),
        "missing_required_points": missing_rows,
        "unofficial_required_points": unofficial,
        "binding_ready": not missing_rows and not unofficial,
        "claim_boundary": (
            "Rail point bindings are ready only when every required simulator "
            "rail point is mapped to an official station identifier from a "
            "documented public or agency source."
        ),
        "remaining_blockers": _binding_blockers(missing_rows, unofficial),
    }


def _binding_blockers(
    missing_rows: Sequence[str],
    unofficial_points: Sequence[str],
) -> list[str]:
    blockers: list[str] = []
    if missing_rows:
        blockers.append(
            "add station-binding rows for required rail points: "
            + ", ".join(missing_rows)
        )
    if unofficial_points:
        blockers.append(
            "replace station-area context rows with official station identifiers "
            "for rail points: "
            + ", ".join(unofficial_points)
        )
    if blockers:
        blockers.append(
            "document station source URL, access date, station code, and any "
            "transformation from the official source"
        )
    return blockers


def _record_from_row(
    row: Mapping[str, str | None],
    path: Path,
    line_num: int,
) -> RailStationBinding:
    values = {column: _clean(row.get(column)) for column in REQUIRED_COLUMNS}
    for column, value in values.items():
        if not value:
            raise ValueError(f"{path}:{line_num} field {column!r} must be non-empty")
    return RailStationBinding(
        binding_id=values["binding_id"],
        region_id=values["region_id"],
        point_id=values["point_id"],
        station_name=values["station_name"],
        station_id=values["station_id"],
        station_code=values["station_code"],
        source_name=values["source_name"],
        source_url_or_citation=values["source_url_or_citation"],
        source_accessed_date=values["source_accessed_date"],
        source_status=values["source_status"],
        claim_scope=values["claim_scope"],
        notes=values["notes"],
    )


def _record_to_row(record: RailStationBinding) -> dict[str, str]:
    return {
        "binding_id": record.binding_id,
        "region_id": record.region_id,
        "point_id": record.point_id,
        "station_name": record.station_name,
        "station_id": record.station_id,
        "station_code": record.station_code,
        "source_name": record.source_name,
        "source_url_or_citation": record.source_url_or_citation,
        "source_accessed_date": record.source_accessed_date,
        "source_status": record.source_status,
        "claim_scope": record.claim_scope,
        "notes": record.notes,
    }


def _validate_record(record: RailStationBinding, path: Path, line_num: int) -> None:
    location = f"{path}:{line_num}"
    if record.source_status not in ALLOWED_SOURCE_STATUSES:
        allowed = ", ".join(sorted(ALLOWED_SOURCE_STATUSES))
        raise ValueError(
            f"{location} has invalid source_status {record.source_status!r}; "
            f"allowed: {allowed}"
        )

    claim_scope = record.claim_scope.lower()
    if record.source_status in NON_OFFICIAL_SOURCE_STATUSES:
        if "not official station-code binding" not in claim_scope:
            raise ValueError(
                f"{location} non-official station row must include "
                "'not official station-code binding' in claim_scope"
            )
    if record.is_official and not _has_official_identifier(record):
        raise ValueError(
            f"{location} official station binding requires station_id or "
            "station_code to be a non-placeholder official identifier"
        )


def _has_official_identifier(record: RailStationBinding) -> bool:
    return not (
        _is_placeholder(record.station_id) and _is_placeholder(record.station_code)
    )


def _is_placeholder(value: str) -> bool:
    return value.strip().lower() in PLACEHOLDER_VALUES


def _validate_columns(fieldnames: Sequence[str] | None, path: Path) -> None:
    if not fieldnames:
        raise ValueError(f"{path} must have a CSV header")
    missing = [column for column in REQUIRED_COLUMNS if column not in fieldnames]
    if missing:
        raise ValueError(f"{path} missing required columns: {', '.join(missing)}")


def _duplicates(values: Iterable[str]) -> set[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return duplicates


def _clean(value: object) -> str:
    return "" if value is None else str(value).strip()


__all__ = [
    "ALLOWED_SOURCE_STATUSES",
    "DEFAULT_RAIL_STATION_BINDING_PATH",
    "NON_OFFICIAL_SOURCE_STATUSES",
    "OFFICIAL_SOURCE_STATUS",
    "REQUIRED_COLUMNS",
    "RailStationBinding",
    "load_rail_station_bindings",
    "summarize_rail_station_bindings",
    "validate_rail_station_bindings",
    "write_rail_station_bindings",
]
