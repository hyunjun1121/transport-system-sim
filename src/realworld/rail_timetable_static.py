"""Normalize reviewed static rail timetable CSV files into cache schema.

This module intentionally requires explicit source-column names. It is a
transformation helper only; it does not make a timetable source accepted rail
evidence by itself.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping

from src.realworld.rail_timetable import (
    REQUIRED_TIMETABLE_COLUMNS,
    load_cached_timetable_events,
)
from src.realworld.source_artifacts import file_sha256


@dataclass(frozen=True)
class StaticTimetableColumnMap:
    """Source CSV columns needed to build normalized station-event rows."""

    trip_id: str
    station_name: str
    station_code: str
    arrival_time: str
    departure_time: str
    direction: str
    service_day: str


@dataclass(frozen=True)
class StaticTimetableSelection:
    """Access/egress station selection and optional source-row filters."""

    access_station_name: str = ""
    access_station_code: str = ""
    egress_station_name: str = ""
    egress_station_code: str = ""
    filters: Mapping[str, str] = field(default_factory=dict)


def normalize_static_timetable_csv(
    input_path: str | Path,
    output_path: str | Path,
    *,
    columns: StaticTimetableColumnMap,
    selection: StaticTimetableSelection,
    encoding: str = "utf-8-sig",
    manifest_path: str | Path | None = None,
) -> dict[str, object]:
    """Normalize a reviewed static timetable CSV into rail cache rows."""

    source_path = Path(input_path)
    target_path = Path(output_path)
    if not source_path.exists():
        raise ValueError(f"input timetable file does not exist: {source_path}")
    if not selection.access_station_name and not selection.access_station_code:
        raise ValueError("access station name or code is required")

    rows = _read_source_rows(source_path, encoding=encoding)
    _validate_source_columns(rows.fieldnames, columns, selection.filters, source_path)

    normalized_rows: list[dict[str, str]] = []
    access_count = 0
    egress_count = 0
    has_egress_selector = bool(selection.egress_station_name or selection.egress_station_code)

    for row_number, row in rows.items:
        if not _row_matches_filters(row, selection.filters):
            continue
        if _row_matches_station(
            row,
            name_column=columns.station_name,
            code_column=columns.station_code,
            station_name=selection.access_station_name,
            station_code=selection.access_station_code,
        ):
            normalized_rows.append(
                _normalized_row(
                    row,
                    columns=columns,
                    station_role="access",
                    event_type="departure",
                    time_column=columns.departure_time,
                    source_path=source_path,
                    row_number=row_number,
                )
            )
            access_count += 1
        if has_egress_selector and _row_matches_station(
            row,
            name_column=columns.station_name,
            code_column=columns.station_code,
            station_name=selection.egress_station_name,
            station_code=selection.egress_station_code,
        ):
            normalized_rows.append(
                _normalized_row(
                    row,
                    columns=columns,
                    station_role="egress",
                    event_type="arrival",
                    time_column=columns.arrival_time,
                    source_path=source_path,
                    row_number=row_number,
                )
            )
            egress_count += 1

    if access_count == 0:
        raise ValueError("no access-station timetable rows matched the selection")
    if has_egress_selector and egress_count == 0:
        raise ValueError("no egress-station timetable rows matched the selection")

    target_path.parent.mkdir(parents=True, exist_ok=True)
    with target_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REQUIRED_TIMETABLE_COLUMNS)
        writer.writeheader()
        writer.writerows(normalized_rows)

    # Re-load through the production cache validator so schema/time errors fail here.
    load_cached_timetable_events(target_path)

    summary = {
        "input_path": str(source_path),
        "input_sha256": file_sha256(source_path),
        "output_path": str(target_path),
        "output_sha256": file_sha256(target_path),
        "normalized_event_count": len(normalized_rows),
        "access_event_count": access_count,
        "egress_event_count": egress_count,
        "source_column_map": columns.__dict__,
        "selection": {
            "access_station_name": selection.access_station_name,
            "access_station_code": selection.access_station_code,
            "egress_station_name": selection.egress_station_name,
            "egress_station_code": selection.egress_station_code,
            "filters": dict(selection.filters),
        },
        "claim_scope": (
            "static timetable normalization cache only; not rail evidence, "
            "not operational service validation, not publication readiness, "
            "not final-study readiness, and not formal acceptance"
        ),
        "publication_ready": False,
        "final_study_ready": False,
        "formal_acceptance_evidence": False,
        "can_mark_complete": False,
        "can_support_rail_evidence_gate": False,
        "source_license_or_provenance_review_status": "not_recorded_by_normalizer",
    }
    if manifest_path is not None:
        manifest = Path(manifest_path)
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text(
            json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return summary


@dataclass(frozen=True)
class _SourceRows:
    fieldnames: tuple[str, ...]
    items: tuple[tuple[int, dict[str, str]], ...]


def _read_source_rows(path: Path, *, encoding: str) -> _SourceRows:
    with path.open("r", encoding=encoding, newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"{path} must have a CSV header")
        items: list[tuple[int, dict[str, str]]] = []
        for row in reader:
            if None in row:
                raise ValueError(f"{path}:{reader.line_num} has too many columns")
            if not any(_clean(value) for value in row.values()):
                continue
            items.append((reader.line_num, {key: _clean(value) for key, value in row.items()}))
    if not items:
        raise ValueError(f"{path} must contain at least one source row")
    return _SourceRows(fieldnames=tuple(reader.fieldnames), items=tuple(items))


def _validate_source_columns(
    fieldnames: tuple[str, ...],
    columns: StaticTimetableColumnMap,
    filters: Mapping[str, str],
    path: Path,
) -> None:
    required = [
        columns.trip_id,
        columns.station_name,
        columns.station_code,
        columns.arrival_time,
        columns.departure_time,
        columns.direction,
        columns.service_day,
        *filters.keys(),
    ]
    missing = [column for column in required if column not in fieldnames]
    if missing:
        raise ValueError(
            f"{path} missing source columns required for normalization: "
            f"{', '.join(sorted(set(missing)))}"
        )


def _row_matches_filters(row: Mapping[str, str], filters: Mapping[str, str]) -> bool:
    return all(_clean(row.get(column)) == _clean(value) for column, value in filters.items())


def _row_matches_station(
    row: Mapping[str, str],
    *,
    name_column: str,
    code_column: str,
    station_name: str,
    station_code: str,
) -> bool:
    name_ok = bool(station_name) and _token(row.get(name_column)) == _token(station_name)
    code_ok = bool(station_code) and _token(row.get(code_column)) == _token(station_code)
    return name_ok or code_ok


def _normalized_row(
    row: Mapping[str, str],
    *,
    columns: StaticTimetableColumnMap,
    station_role: str,
    event_type: str,
    time_column: str,
    source_path: Path,
    row_number: int,
) -> dict[str, str]:
    values = {
        "trip_id": _clean(row.get(columns.trip_id)),
        "station_role": station_role,
        "station_name": _clean(row.get(columns.station_name)),
        "station_code": _clean(row.get(columns.station_code)),
        "event_time": _clean(row.get(time_column)),
        "event_type": event_type,
        "direction": _clean(row.get(columns.direction)),
        "service_day": _clean(row.get(columns.service_day)),
    }
    missing = [column for column, value in values.items() if not value]
    if missing:
        raise ValueError(
            f"{source_path}:{row_number} cannot normalize {station_role} "
            f"{event_type}; missing {', '.join(missing)}"
        )
    return values


def _clean(value: object) -> str:
    return "" if value is None else str(value).strip()


def _token(value: object) -> str:
    return _clean(value).casefold()


__all__ = [
    "StaticTimetableColumnMap",
    "StaticTimetableSelection",
    "normalize_static_timetable_csv",
]
