"""Diagnostic segment-pair probe for retained static rail timetables.

This module reads the retained Seoul Metro static timetable CSV directly and
computes a bounded segment-pair diagnostic. It intentionally does not write
``rail_service_evidence.csv`` and does not close rail evidence gates.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from math import ceil, floor
from pathlib import Path
from statistics import median
from typing import Any, Iterable, Mapping, Sequence

from src.realworld.rail_timetable import parse_service_time_min
from src.realworld.source_artifacts import file_sha256


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_STATIC_TIMETABLE_SOURCE_PATH = (
    PROJECT_ROOT / "data" / "rail" / "pilot_rail_timetable_static_source.csv"
)
DEFAULT_DIAGNOSTIC_CSV_PATH = (
    PROJECT_ROOT
    / "data"
    / "rail"
    / "pilot_rail_static_timetable_segment_pair_diagnostic.csv"
)
DEFAULT_DIAGNOSTIC_MANIFEST_PATH = (
    PROJECT_ROOT
    / "data"
    / "rail"
    / "pilot_rail_static_timetable_segment_pair_diagnostic_manifest.json"
)
DEFAULT_DIAGNOSTIC_DOC_PATH = (
    PROJECT_ROOT / "docs" / "rail_static_timetable_segment_pair_diagnostic.md"
)

CLAIM_BOUNDARY = (
    "Static timetable segment-pair diagnostic only; not rail-service evidence, "
    "not observed transfer calibration, not source/provenance acceptance, not "
    "license certification, not operational routing, not publication readiness, "
    "not final-study readiness, and not formal acceptance."
)

DIAGNOSTIC_COLUMNS: tuple[str, ...] = (
    "row_type",
    "segment_id",
    "line",
    "direction",
    "service_day",
    "origin_station_name",
    "origin_station_id",
    "destination_station_name",
    "destination_station_id",
    "matched_trip_count",
    "median_segment_minutes",
    "min_segment_minutes",
    "max_segment_minutes",
    "p90_segment_minutes",
    "assumed_transfer_buffer_minutes",
    "feasible_connection_count",
    "median_connection_wait_minutes",
    "median_total_minutes",
    "min_total_minutes",
    "max_total_minutes",
    "p90_total_minutes",
    "claim_boundary",
    "notes",
)


@dataclass(frozen=True)
class SegmentSpec:
    """One same-line station-to-station segment extracted from source rows."""

    segment_id: str
    line: str
    direction: str
    service_day: str
    origin_station_name: str
    origin_station_id: str
    destination_station_name: str
    destination_station_id: str


@dataclass(frozen=True)
class MatchedSegmentTrip:
    """One same-train segment match from origin departure to destination arrival."""

    trip_id: str
    origin_departure_min: float
    destination_arrival_min: float
    travel_time_min: float


DEFAULT_SEGMENT_SPECS: tuple[SegmentSpec, SegmentSpec] = (
    SegmentSpec(
        segment_id="line9_olympic_park_to_seokchon",
        line="9",
        direction="DOWN",
        service_day="DAY",
        origin_station_name="올림픽공원",
        origin_station_id="4136",
        destination_station_name="석촌",
        destination_station_id="4133",
    ),
    SegmentSpec(
        segment_id="line8_seokchon_to_jamsil",
        line="8",
        direction="UP",
        service_day="DAY",
        origin_station_name="석촌",
        origin_station_id="2816",
        destination_station_name="잠실",
        destination_station_id="2815",
    ),
)


def build_static_timetable_segment_pair_diagnostic(
    source_path: str | Path = DEFAULT_STATIC_TIMETABLE_SOURCE_PATH,
    *,
    segment_specs: Sequence[SegmentSpec] = DEFAULT_SEGMENT_SPECS,
    assumed_transfer_buffer_min: float = 5.0,
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    """Build diagnostic CSV rows and manifest data from a static timetable."""

    if len(segment_specs) != 2:
        raise ValueError("segment-pair diagnostic requires exactly two segment specs")
    if assumed_transfer_buffer_min < 0.0:
        raise ValueError("assumed_transfer_buffer_min must be non-negative")

    source = Path(source_path)
    source_rows, fieldnames = _read_source_rows(source)
    segment_matches = [
        _match_segment_trips(source_rows, spec)
        for spec in segment_specs
    ]
    if any(not matches for matches in segment_matches):
        missing = [
            spec.segment_id
            for spec, matches in zip(segment_specs, segment_matches)
            if not matches
        ]
        raise ValueError(f"no positive matched timetable rows for: {', '.join(missing)}")

    connections = _connect_segments(
        segment_matches[0],
        segment_matches[1],
        assumed_transfer_buffer_min=assumed_transfer_buffer_min,
    )
    rows = [
        _segment_row(segment_specs[0], segment_matches[0]),
        _segment_row(segment_specs[1], segment_matches[1]),
        _pair_row(
            segment_specs,
            connections,
            assumed_transfer_buffer_min=assumed_transfer_buffer_min,
        ),
    ]
    manifest = {
        "schema_version": 1,
        "claim_boundary": CLAIM_BOUNDARY,
        "diagnostic_only": True,
        "publication_ready": False,
        "final_study_ready": False,
        "formal_acceptance_evidence": False,
        "can_mark_complete": False,
        "can_support_rail_evidence_gate": False,
        "can_support_transfer_evidence_gate": False,
        "source_path": _display_path(source),
        "source_sha256": file_sha256(source),
        "source_size_bytes": source.stat().st_size,
        "source_columns": list(fieldnames),
        "station_identifier_namespace": "SI_ID from the retained static timetable CSV",
        "time_column_semantics": {
            "origin_departure": "EDT",
            "destination_arrival": "STT",
        },
        "segment_specs": [_segment_spec_manifest(spec) for spec in segment_specs],
        "segment_match_counts": {
            spec.segment_id: len(matches)
            for spec, matches in zip(segment_specs, segment_matches)
        },
        "assumed_transfer_buffer_min": assumed_transfer_buffer_min,
        "feasible_connection_count": len(connections),
        "row_count": len(rows),
        "review_items": [
            "Review station identifier namespace and line/direction filters before use.",
            "Do not treat this diagnostic as observed transfer walking, platform circulation, or crowding evidence.",
            "Do not write rail_service_evidence.csv from this diagnostic without separate source-backed review.",
            "Keep publication, final-study, rail-evidence, transfer-evidence, and formal-acceptance gates blocked.",
        ],
        "remaining_blockers": [
            "Seokchon transfer walking, wait, circulation, and crowding are not source-backed or observed.",
            "Rail source decisions remain pending for source-backed timing evidence.",
            "This diagnostic does not validate rail capacity or emergency rail availability.",
            "Formal source/provenance and license acceptance remain absent.",
        ],
    }
    if connections:
        totals = [connection["total_min"] for connection in connections]
        waits = [connection["connection_wait_min"] for connection in connections]
        manifest["connection_summary"] = {
            "median_total_min": _round(median(totals)),
            "min_total_min": _round(min(totals)),
            "max_total_min": _round(max(totals)),
            "p90_total_min": _round(_percentile(totals, 0.9)),
            "median_connection_wait_min": _round(median(waits)),
        }
    else:
        manifest["connection_summary"] = {}
        manifest["remaining_blockers"].append(
            "No feasible same-day segment-pair connections were found with the assumed transfer buffer."
        )
    return rows, manifest


def write_static_timetable_segment_pair_diagnostic(
    *,
    source_path: str | Path = DEFAULT_STATIC_TIMETABLE_SOURCE_PATH,
    output_path: str | Path = DEFAULT_DIAGNOSTIC_CSV_PATH,
    manifest_path: str | Path = DEFAULT_DIAGNOSTIC_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_DIAGNOSTIC_DOC_PATH,
    assumed_transfer_buffer_min: float = 5.0,
) -> dict[str, Any]:
    """Write diagnostic CSV, manifest, and Markdown artifacts."""

    rows, manifest = build_static_timetable_segment_pair_diagnostic(
        source_path,
        assumed_transfer_buffer_min=assumed_transfer_buffer_min,
    )
    output = Path(output_path)
    manifest_file = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest_file.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=DIAGNOSTIC_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    manifest["outputs"] = {
        "csv": _display_path(output),
        "manifest": _display_path(manifest_file),
        "doc": _display_path(doc),
    }
    manifest_file.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    doc.write_text(_markdown(manifest, rows), encoding="utf-8")
    return manifest


def _read_source_rows(path: Path) -> tuple[list[dict[str, str]], tuple[str, ...]]:
    if not path.exists():
        raise ValueError(f"static timetable source does not exist: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"{path} must have a CSV header")
        missing = [
            column
            for column in (
                "LINE",
                "SI_ID",
                "STATION_NM",
                "WEEKTAG",
                "INOUTTAG",
                "TRAIN_NO",
                "STT",
                "EDT",
            )
            if column not in reader.fieldnames
        ]
        if missing:
            raise ValueError(f"{path} missing source columns: {', '.join(missing)}")
        rows = [
            {key: str(value or "").strip() for key, value in row.items() if key is not None}
            for row in reader
            if row and any(str(value or "").strip() for value in row.values())
        ]
    if not rows:
        raise ValueError(f"{path} must contain source rows")
    return rows, tuple(reader.fieldnames)


def _match_segment_trips(
    rows: Sequence[Mapping[str, str]],
    spec: SegmentSpec,
) -> list[MatchedSegmentTrip]:
    by_trip: dict[str, dict[str, Mapping[str, str]]] = {}
    for row in rows:
        if row.get("LINE") != spec.line:
            continue
        if row.get("INOUTTAG") != spec.direction:
            continue
        if row.get("WEEKTAG") != spec.service_day:
            continue
        station_id = row.get("SI_ID")
        if station_id not in {spec.origin_station_id, spec.destination_station_id}:
            continue
        trip_id = row.get("TRAIN_NO", "")
        if not trip_id:
            continue
        key = "origin" if station_id == spec.origin_station_id else "destination"
        by_trip.setdefault(trip_id, {})[key] = row

    matches: list[MatchedSegmentTrip] = []
    for trip_id, values in by_trip.items():
        origin = values.get("origin")
        destination = values.get("destination")
        if origin is None or destination is None:
            continue
        depart = parse_service_time_min(origin["EDT"])
        arrive = parse_service_time_min(destination["STT"])
        travel = _positive_elapsed(arrive, depart)
        if travel <= 0.0:
            continue
        matches.append(
            MatchedSegmentTrip(
                trip_id=trip_id,
                origin_departure_min=depart,
                destination_arrival_min=arrive,
                travel_time_min=travel,
            )
        )
    return sorted(matches, key=lambda item: item.origin_departure_min)


def _connect_segments(
    first: Sequence[MatchedSegmentTrip],
    second: Sequence[MatchedSegmentTrip],
    *,
    assumed_transfer_buffer_min: float,
) -> list[dict[str, float | str]]:
    second_by_departure = sorted(second, key=lambda item: item.origin_departure_min)
    connections: list[dict[str, float | str]] = []
    for first_trip in first:
        earliest_second_departure = (
            first_trip.destination_arrival_min + assumed_transfer_buffer_min
        )
        candidate = next(
            (
                second_trip
                for second_trip in second_by_departure
                if second_trip.origin_departure_min >= earliest_second_departure
            ),
            None,
        )
        if candidate is None:
            continue
        total = _positive_elapsed(
            candidate.destination_arrival_min,
            first_trip.origin_departure_min,
        )
        wait = candidate.origin_departure_min - first_trip.destination_arrival_min
        if wait < 0.0:
            wait += 24.0 * 60.0
        connections.append(
            {
                "first_trip_id": first_trip.trip_id,
                "second_trip_id": candidate.trip_id,
                "connection_wait_min": wait,
                "total_min": total,
            }
        )
    return connections


def _segment_row(
    spec: SegmentSpec,
    matches: Sequence[MatchedSegmentTrip],
) -> dict[str, str]:
    values = [match.travel_time_min for match in matches]
    return _blank_row(
        row_type="segment",
        segment_id=spec.segment_id,
        line=spec.line,
        direction=spec.direction,
        service_day=spec.service_day,
        origin_station_name=spec.origin_station_name,
        origin_station_id=spec.origin_station_id,
        destination_station_name=spec.destination_station_name,
        destination_station_id=spec.destination_station_id,
        matched_trip_count=str(len(matches)),
        median_segment_minutes=_fmt(median(values)),
        min_segment_minutes=_fmt(min(values)),
        max_segment_minutes=_fmt(max(values)),
        p90_segment_minutes=_fmt(_percentile(values, 0.9)),
        notes="Same-train station-to-station segment timing from static timetable rows.",
    )


def _pair_row(
    segment_specs: Sequence[SegmentSpec],
    connections: Sequence[Mapping[str, float | str]],
    *,
    assumed_transfer_buffer_min: float,
) -> dict[str, str]:
    first, second = segment_specs
    row = _blank_row(
        row_type="segment_pair_with_assumed_transfer_buffer",
        segment_id=f"{first.segment_id}+{second.segment_id}",
        line=f"{first.line}+{second.line}",
        direction=f"{first.direction}+{second.direction}",
        service_day=first.service_day,
        origin_station_name=first.origin_station_name,
        origin_station_id=first.origin_station_id,
        destination_station_name=second.destination_station_name,
        destination_station_id=second.destination_station_id,
        assumed_transfer_buffer_minutes=_fmt(assumed_transfer_buffer_min),
        feasible_connection_count=str(len(connections)),
        notes=(
            "Connection diagnostic uses an assumed transfer buffer only; it is "
            "not observed transfer walking, circulation, crowding, or calibration evidence."
        ),
    )
    if connections:
        totals = [float(connection["total_min"]) for connection in connections]
        waits = [float(connection["connection_wait_min"]) for connection in connections]
        row.update(
            {
                "median_connection_wait_minutes": _fmt(median(waits)),
                "median_total_minutes": _fmt(median(totals)),
                "min_total_minutes": _fmt(min(totals)),
                "max_total_minutes": _fmt(max(totals)),
                "p90_total_minutes": _fmt(_percentile(totals, 0.9)),
            }
        )
    return row


def _blank_row(**updates: str) -> dict[str, str]:
    row = {column: "" for column in DIAGNOSTIC_COLUMNS}
    row["claim_boundary"] = CLAIM_BOUNDARY
    row.update(updates)
    return row


def _segment_spec_manifest(spec: SegmentSpec) -> dict[str, str]:
    return {
        "segment_id": spec.segment_id,
        "line": spec.line,
        "direction": spec.direction,
        "service_day": spec.service_day,
        "origin_station_name": spec.origin_station_name,
        "origin_station_id": spec.origin_station_id,
        "destination_station_name": spec.destination_station_name,
        "destination_station_id": spec.destination_station_id,
    }


def _positive_elapsed(arrive_min: float, depart_min: float) -> float:
    elapsed = arrive_min - depart_min
    if elapsed < 0.0:
        elapsed += 24.0 * 60.0
    return elapsed


def _percentile(values: Iterable[float], q: float) -> float:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("cannot compute percentile of empty values")
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * q
    lower = floor(position)
    upper = ceil(position)
    if lower == upper:
        return ordered[int(position)]
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def _round(value: float) -> float:
    return round(float(value), 3)


def _fmt(value: float) -> str:
    rounded = _round(value)
    if rounded.is_integer():
        return str(int(rounded))
    return f"{rounded:.3f}".rstrip("0").rstrip(".")


def _display_path(path: str | Path) -> str:
    value = Path(path)
    try:
        return value.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return value.as_posix()


def _markdown(manifest: Mapping[str, Any], rows: Sequence[Mapping[str, str]]) -> str:
    lines = [
        "# Rail Static Timetable Segment-Pair Diagnostic",
        "",
        str(manifest["claim_boundary"]),
        "",
        "## Verdict",
        "",
        f"- Diagnostic only: `{str(manifest['diagnostic_only']).lower()}`",
        f"- Publication ready: `{str(manifest['publication_ready']).lower()}`",
        f"- Final-study ready: `{str(manifest['final_study_ready']).lower()}`",
        f"- Can support rail evidence gate: `{str(manifest['can_support_rail_evidence_gate']).lower()}`",
        f"- Source: `{manifest['source_path']}`",
        f"- Source SHA256: `{manifest['source_sha256']}`",
        f"- Assumed transfer buffer: `{manifest['assumed_transfer_buffer_min']}` minutes",
        f"- Feasible diagnostic connections: `{manifest['feasible_connection_count']}`",
        "",
        "## Rows",
        "",
        "| Type | Segment | Trips | Median segment | Feasible connections | Median total | Notes |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            "| {row_type} | {segment_id} | {trips} | {segment} | {connections} | {total} | {notes} |".format(
                row_type=_cell(row["row_type"]),
                segment_id=_cell(row["segment_id"]),
                trips=_cell(row["matched_trip_count"]),
                segment=_cell(row["median_segment_minutes"]),
                connections=_cell(row["feasible_connection_count"]),
                total=_cell(row["median_total_minutes"]),
                notes=_cell(row["notes"]),
            )
        )
    lines.extend(
        [
            "",
            "## Remaining Blockers",
            "",
            *[f"- {item}" for item in manifest["remaining_blockers"]],
            "",
        ]
    )
    return "\n".join(lines)


def _cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", "<br>")


__all__ = [
    "CLAIM_BOUNDARY",
    "DEFAULT_DIAGNOSTIC_CSV_PATH",
    "DEFAULT_DIAGNOSTIC_DOC_PATH",
    "DEFAULT_DIAGNOSTIC_MANIFEST_PATH",
    "DEFAULT_SEGMENT_SPECS",
    "DEFAULT_STATIC_TIMETABLE_SOURCE_PATH",
    "DIAGNOSTIC_COLUMNS",
    "SegmentSpec",
    "build_static_timetable_segment_pair_diagnostic",
    "write_static_timetable_segment_pair_diagnostic",
]
