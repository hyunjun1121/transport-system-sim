"""Derive rail-service evidence from cached static GTFS feeds.

This module reads a reviewed GTFS zip or directory without live API calls and
converts selected stop-to-stop trips into the repository rail evidence schema.
It is intentionally small: it derives headway and scheduled in-vehicle travel
time only, while capacity remains a supplied sensitivity or reviewed value.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from io import TextIOWrapper
import json
from pathlib import Path
from statistics import median
from typing import Any, Iterable, Mapping, Sequence
import zipfile

from src.realworld.rail_evidence import RailServiceEvidence
from src.realworld.source_artifacts import (
    file_sha256 as _source_file_sha256,
    validate_sha256,
    validate_loaded_source_matches_metadata,
)
from src.realworld.rail_timetable import parse_service_time_min


REQUIRED_GTFS_FILES: tuple[str, ...] = ("stops.txt", "trips.txt", "stop_times.txt")
REQUIRED_STOPS_COLUMNS: tuple[str, ...] = ("stop_id", "stop_name")
REQUIRED_TRIPS_COLUMNS: tuple[str, ...] = ("trip_id", "route_id", "service_id")
REQUIRED_STOP_TIMES_COLUMNS: tuple[str, ...] = (
    "trip_id",
    "arrival_time",
    "departure_time",
    "stop_id",
    "stop_sequence",
)


@dataclass(frozen=True)
class GtfsStop:
    """One GTFS stop row needed for rail evidence derivation."""

    stop_id: str
    stop_name: str


@dataclass(frozen=True)
class GtfsTrip:
    """One GTFS trip row needed for rail evidence derivation."""

    trip_id: str
    route_id: str
    service_id: str
    direction_id: str = ""


@dataclass(frozen=True)
class GtfsStopTime:
    """One GTFS stop time row needed for rail evidence derivation."""

    trip_id: str
    stop_id: str
    arrival_time_min: float
    departure_time_min: float
    stop_sequence: int


@dataclass(frozen=True)
class CachedGtfsFeed:
    """Normalized subset of a cached static GTFS feed."""

    source_path: str
    stops: Mapping[str, GtfsStop]
    trips: Mapping[str, GtfsTrip]
    stop_times_by_trip: Mapping[str, tuple[GtfsStopTime, ...]]


@dataclass(frozen=True)
class GtfsEvidenceDerivationConfig:
    """Metadata and filters for one GTFS-derived rail evidence row."""

    evidence_id: str
    region_id: str
    access_point: str
    egress_point: str
    access_stop_id: str
    egress_stop_id: str
    source_name: str
    source_url_or_citation: str
    extraction_date: str
    capacity_pax_per_train: float
    service_window: str
    route_id: str = ""
    service_ids: tuple[str, ...] = ()
    direction_id: str = ""
    source_artifact_path: str = ""
    source_artifact_sha256: str = ""
    gtfs_validator_report_path: str = ""
    gtfs_validator_report_sha256: str = ""


def load_cached_gtfs_feed(path: str | Path) -> CachedGtfsFeed:
    """Load the GTFS files needed for rail headway and travel-time evidence."""

    source = Path(path)
    if source.is_dir():
        return _load_gtfs_directory(source)
    if source.is_file() and zipfile.is_zipfile(source):
        return _load_gtfs_zip(source)
    raise ValueError(f"{source} must be a GTFS directory or zip file")


def derive_rail_service_evidence_from_gtfs(
    feed: CachedGtfsFeed,
    config: GtfsEvidenceDerivationConfig,
) -> RailServiceEvidence:
    """Derive scheduled headway and stop-to-stop travel time from cached GTFS."""

    if config.capacity_pax_per_train <= 0.0:
        raise ValueError("capacity_pax_per_train must be positive")
    if not config.source_artifact_path or not config.source_artifact_sha256:
        raise ValueError(
            "source_artifact_path and source_artifact_sha256 are required for "
            "cached GTFS-derived rail evidence"
        )
    validate_loaded_source_matches_metadata(
        feed.source_path,
        config.source_artifact_path,
        expected_sha256=config.source_artifact_sha256,
    )
    if not config.gtfs_validator_report_path or not config.gtfs_validator_report_sha256:
        raise ValueError(
            "gtfs_validator_report_path and gtfs_validator_report_sha256 are "
            "required for cached GTFS-derived rail evidence"
        )
    validator_summary = validate_gtfs_validator_report(
        config.gtfs_validator_report_path,
        expected_sha256=config.gtfs_validator_report_sha256,
        expected_feed_sha256=config.source_artifact_sha256,
    )
    access_stop = feed.stops.get(config.access_stop_id)
    egress_stop = feed.stops.get(config.egress_stop_id)
    if access_stop is None:
        raise ValueError(f"access_stop_id {config.access_stop_id!r} not found in GTFS stops")
    if egress_stop is None:
        raise ValueError(f"egress_stop_id {config.egress_stop_id!r} not found in GTFS stops")

    trip_ids = _eligible_trip_ids(feed.trips.values(), config)
    if not trip_ids:
        raise ValueError("no GTFS trips match the configured route/service/direction filters")

    pairs = _paired_stop_times(
        feed,
        trip_ids=trip_ids,
        access_stop_id=config.access_stop_id,
        egress_stop_id=config.egress_stop_id,
    )
    if not pairs:
        raise ValueError("no GTFS trips contain access and egress stops in sequence")
    if len(pairs) < 2:
        raise ValueError("at least two GTFS trips are required to derive headway")

    access_departures = sorted(access.departure_time_min for access, _egress in pairs)
    headways = [
        access_departures[index + 1] - access_departures[index]
        for index in range(len(access_departures) - 1)
    ]
    if any(headway <= 0.0 for headway in headways):
        raise ValueError("GTFS access departures must be strictly increasing after filtering")

    travel_times = [
        _positive_time_delta(egress.arrival_time_min, access.departure_time_min)
        for access, egress in pairs
    ]

    return RailServiceEvidence(
        evidence_id=config.evidence_id,
        region_id=config.region_id,
        access_point=config.access_point,
        egress_point=config.egress_point,
        access_station_name=access_stop.stop_name,
        egress_station_name=egress_stop.stop_name,
        source_status="cached_gtfs_derived",
        source_name=config.source_name,
        source_url_or_citation=config.source_url_or_citation,
        extraction_date=config.extraction_date,
        headway_min=float(median(headways)),
        travel_time_min=float(median(travel_times)),
        capacity_pax_per_train=float(config.capacity_pax_per_train),
        service_window=config.service_window,
        claim_scope=(
            "cached GTFS-derived rail timing evidence; capacity remains "
            "sensitivity-only unless separately sourced; not operational forecast"
        ),
        notes=(
            f"Derived from {len(pairs)} GTFS trips between "
            f"{config.access_stop_id} and {config.egress_stop_id}. "
            f"Filters: route_id={config.route_id or 'any'}, "
            f"service_ids={';'.join(config.service_ids) or 'any'}, "
            f"direction_id={config.direction_id or 'any'}. "
            f"source_artifact_path={config.source_artifact_path}; "
            f"source_artifact_sha256={config.source_artifact_sha256}; "
            f"gtfs_validator_report_path={config.gtfs_validator_report_path}; "
            f"gtfs_validator_report_sha256={config.gtfs_validator_report_sha256}; "
            f"gtfs_validator_feed_sha256={validator_summary['feed_sha256']}; "
            f"gtfs_validator_error_count={validator_summary['error_count']}; "
            f"gtfs_validator_warning_count={validator_summary['warning_count']}."
        ),
        derived_fields="headway;travel_time",
        source_artifact_path=config.source_artifact_path,
        source_artifact_sha256=config.source_artifact_sha256,
        gtfs_validator_report_path=config.gtfs_validator_report_path,
        gtfs_validator_report_sha256=config.gtfs_validator_report_sha256,
    )


def file_sha256(path: str | Path) -> str:
    """Return the SHA256 digest for a cached GTFS artifact file."""

    return _source_file_sha256(path)


def summarize_gtfs_validator_report(path: str | Path) -> dict[str, Any]:
    """Return conservative counts from a retained GTFS Validator JSON report."""

    report_path = Path(path)
    with report_path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("GTFS Validator report must be a JSON object")

    counts = _validator_counts(value)
    feed_sha256 = _validator_feed_sha256(value)
    validator_version = (
        _clean(value.get("validatorVersion"))
        or _clean(value.get("validator"))
        or _clean(_nested(value, ("summary", "validatorVersion")))
    )
    return {
        "path": str(report_path),
        "sha256": file_sha256(report_path),
        "feed_sha256": feed_sha256,
        "validator_version": validator_version,
        "error_count": counts["errors"],
        "warning_count": counts["warnings"],
        "info_count": counts["infos"],
        "total_notice_count": counts["total"],
        "validation_report_ready": counts["errors"] == 0,
    }


def validate_gtfs_validator_report(
    path: str | Path,
    *,
    expected_sha256: str = "",
    expected_feed_sha256: str = "",
) -> dict[str, Any]:
    """Validate that a retained GTFS Validator report has zero errors."""

    summary = summarize_gtfs_validator_report(path)
    if expected_sha256 and summary["sha256"].lower() != expected_sha256.lower():
        raise ValueError("GTFS Validator report SHA256 does not match metadata")
    if expected_feed_sha256:
        if not summary["feed_sha256"]:
            raise ValueError(
                "GTFS Validator report must record the validated GTFS feed SHA256"
            )
        if summary["feed_sha256"].lower() != expected_feed_sha256.lower():
            raise ValueError(
                "GTFS Validator report feed SHA256 does not match source artifact"
            )
    if summary["error_count"] > 0:
        raise ValueError(
            f"GTFS Validator report has {summary['error_count']} error notices"
        )
    return summary


def _load_gtfs_directory(source: Path) -> CachedGtfsFeed:
    for filename in REQUIRED_GTFS_FILES:
        if not (source / filename).is_file():
            raise ValueError(f"{source} missing required GTFS file {filename}")
    stops = _load_stops(source / "stops.txt")
    trips = _load_trips(source / "trips.txt")
    stop_times = _load_stop_times(source / "stop_times.txt")
    return CachedGtfsFeed(
        source_path=str(source),
        stops=stops,
        trips=trips,
        stop_times_by_trip=stop_times,
    )


def _load_gtfs_zip(source: Path) -> CachedGtfsFeed:
    with zipfile.ZipFile(source, "r") as archive:
        names = set(archive.namelist())
        missing = [filename for filename in REQUIRED_GTFS_FILES if filename not in names]
        if missing:
            raise ValueError(
                f"{source} missing required GTFS files: {', '.join(missing)}"
            )
        with archive.open("stops.txt", "r") as raw:
            stops = _load_stops(TextIOWrapper(raw, encoding="utf-8-sig"), source)
        with archive.open("trips.txt", "r") as raw:
            trips = _load_trips(TextIOWrapper(raw, encoding="utf-8-sig"), source)
        with archive.open("stop_times.txt", "r") as raw:
            stop_times = _load_stop_times(TextIOWrapper(raw, encoding="utf-8-sig"), source)
    return CachedGtfsFeed(
        source_path=str(source),
        stops=stops,
        trips=trips,
        stop_times_by_trip=stop_times,
    )


def _load_stops(path_or_handle: Path | TextIOWrapper, source: Path | None = None) -> dict[str, GtfsStop]:
    rows = _read_csv_rows(path_or_handle, REQUIRED_STOPS_COLUMNS, source)
    stops: dict[str, GtfsStop] = {}
    for line_num, row in rows:
        stop_id = _required(row, "stop_id", line_num)
        stops[stop_id] = GtfsStop(
            stop_id=stop_id,
            stop_name=_required(row, "stop_name", line_num),
        )
    if not stops:
        raise ValueError("GTFS stops.txt must contain at least one stop")
    return stops


def _load_trips(path_or_handle: Path | TextIOWrapper, source: Path | None = None) -> dict[str, GtfsTrip]:
    rows = _read_csv_rows(path_or_handle, REQUIRED_TRIPS_COLUMNS, source)
    trips: dict[str, GtfsTrip] = {}
    for line_num, row in rows:
        trip_id = _required(row, "trip_id", line_num)
        trips[trip_id] = GtfsTrip(
            trip_id=trip_id,
            route_id=_required(row, "route_id", line_num),
            service_id=_required(row, "service_id", line_num),
            direction_id=_clean(row.get("direction_id")),
        )
    if not trips:
        raise ValueError("GTFS trips.txt must contain at least one trip")
    return trips


def _load_stop_times(
    path_or_handle: Path | TextIOWrapper,
    source: Path | None = None,
) -> dict[str, tuple[GtfsStopTime, ...]]:
    rows = _read_csv_rows(path_or_handle, REQUIRED_STOP_TIMES_COLUMNS, source)
    by_trip: dict[str, list[GtfsStopTime]] = {}
    for line_num, row in rows:
        trip_id = _required(row, "trip_id", line_num)
        by_trip.setdefault(trip_id, []).append(
            GtfsStopTime(
                trip_id=trip_id,
                stop_id=_required(row, "stop_id", line_num),
                arrival_time_min=parse_service_time_min(
                    _required(row, "arrival_time", line_num)
                ),
                departure_time_min=parse_service_time_min(
                    _required(row, "departure_time", line_num)
                ),
                stop_sequence=_positive_int(
                    _required(row, "stop_sequence", line_num),
                    "stop_sequence",
                    line_num,
                ),
            )
        )
    if not by_trip:
        raise ValueError("GTFS stop_times.txt must contain at least one row")
    return {
        trip_id: tuple(sorted(rows, key=lambda item: item.stop_sequence))
        for trip_id, rows in by_trip.items()
    }


def _read_csv_rows(
    path_or_handle: Path | TextIOWrapper,
    required_columns: Sequence[str],
    source: Path | None = None,
) -> list[tuple[int, Mapping[str, str | None]]]:
    if isinstance(path_or_handle, Path):
        with path_or_handle.open("r", encoding="utf-8-sig", newline="") as handle:
            return _read_csv_rows_from_handle(handle, required_columns, path_or_handle)
    return _read_csv_rows_from_handle(path_or_handle, required_columns, source)


def _read_csv_rows_from_handle(
    handle: TextIOWrapper,
    required_columns: Sequence[str],
    source: Path | None,
) -> list[tuple[int, Mapping[str, str | None]]]:
    reader = csv.DictReader(handle)
    label = str(source or "GTFS feed")
    if not reader.fieldnames:
        raise ValueError(f"{label} must have a CSV header")
    missing = [column for column in required_columns if column not in reader.fieldnames]
    if missing:
        raise ValueError(f"{label} missing required columns: {', '.join(missing)}")
    rows: list[tuple[int, Mapping[str, str | None]]] = []
    for row in reader:
        if None in row:
            raise ValueError(f"{label}:{reader.line_num} has too many columns")
        if any(_clean(value) for value in row.values()):
            rows.append((reader.line_num, row))
    return rows


def _eligible_trip_ids(
    trips: Iterable[GtfsTrip],
    config: GtfsEvidenceDerivationConfig,
) -> set[str]:
    return {
        trip.trip_id
        for trip in trips
        if (not config.route_id or trip.route_id == config.route_id)
        and (not config.service_ids or trip.service_id in config.service_ids)
        and (not config.direction_id or trip.direction_id == config.direction_id)
    }


def _paired_stop_times(
    feed: CachedGtfsFeed,
    *,
    trip_ids: set[str],
    access_stop_id: str,
    egress_stop_id: str,
) -> list[tuple[GtfsStopTime, GtfsStopTime]]:
    pairs: list[tuple[GtfsStopTime, GtfsStopTime]] = []
    for trip_id in sorted(trip_ids):
        rows = feed.stop_times_by_trip.get(trip_id, ())
        access_rows = [row for row in rows if row.stop_id == access_stop_id]
        egress_rows = [row for row in rows if row.stop_id == egress_stop_id]
        if not access_rows or not egress_rows:
            continue
        access = access_rows[0]
        egress = egress_rows[0]
        if access.stop_sequence < egress.stop_sequence:
            pairs.append((access, egress))
    return pairs


def _positive_time_delta(arrival_min: float, departure_min: float) -> float:
    delta = arrival_min - departure_min
    if delta < 0.0:
        delta += 24.0 * 60.0
    if delta <= 0.0:
        raise ValueError("GTFS stop-to-stop travel time must be positive")
    return delta


def _positive_int(value: str, field: str, line_num: int) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise ValueError(f"GTFS line {line_num} field {field!r} must be an integer") from exc
    if parsed <= 0:
        raise ValueError(f"GTFS line {line_num} field {field!r} must be positive")
    return parsed


def _required(row: Mapping[str, str | None], field: str, line_num: int) -> str:
    value = _clean(row.get(field))
    if not value:
        raise ValueError(f"GTFS line {line_num} field {field!r} must be non-empty")
    return value


def _clean(value: object) -> str:
    return "" if value is None else str(value).strip()


def _validator_counts(value: Mapping[str, Any]) -> dict[str, int]:
    summary_counts = _nested(value, ("summary", "counts"))
    if isinstance(summary_counts, Mapping):
        if "errors" not in summary_counts:
            raise ValueError("GTFS Validator report counts must include errors")
        errors = _int_value(summary_counts.get("errors"))
        warnings = _int_value(summary_counts.get("warnings"))
        infos = _first_int_value(summary_counts, "infos", "info")
        return {
            "errors": errors,
            "warnings": warnings,
            "infos": infos,
            "total": _total_count(summary_counts, errors, warnings, infos),
        }

    if any(key in value for key in ("errors", "warnings", "infos", "info", "total")):
        if "errors" not in value:
            raise ValueError("GTFS Validator report counts must include errors")
        errors = _int_value(value.get("errors"))
        warnings = _int_value(value.get("warnings"))
        infos = _first_int_value(value, "infos", "info")
        return {
            "errors": errors,
            "warnings": warnings,
            "infos": infos,
            "total": _total_count(value, errors, warnings, infos),
        }

    notices = value.get("notices")
    if isinstance(notices, list):
        errors = warnings = infos = total = 0
        for notice in notices:
            if not isinstance(notice, Mapping):
                raise ValueError("GTFS Validator notices must be JSON objects")
            notice_total = _int_value(
                notice.get("totalNotices", notice.get("total", 1))
            )
            severity = (
                _clean(notice.get("severity"))
                or _clean(notice.get("severityString"))
            ).upper()
            if severity == "ERROR":
                errors += notice_total
            elif severity == "WARNING":
                warnings += notice_total
            elif severity == "INFO":
                infos += notice_total
            else:
                raise ValueError(
                    "GTFS Validator notice severity must be ERROR, WARNING, or INFO"
                )
            total += notice_total
        return {
            "errors": errors,
            "warnings": warnings,
            "infos": infos,
            "total": total,
        }

    raise ValueError(
        "GTFS Validator report must include summary.counts, top-level counts, or notices"
    )


def _validator_feed_sha256(value: Mapping[str, Any]) -> str:
    for candidate in (
        value.get("source_artifact_sha256"),
        value.get("gtfs_feed_sha256"),
        value.get("feed_sha256"),
        value.get("input_sha256"),
        _nested(value, ("input", "sha256")),
        _nested(value, ("source", "sha256")),
        _nested(value, ("feed", "sha256")),
        _nested(value, ("feedInfo", "sha256")),
        _nested(value, ("metadata", "source_artifact_sha256")),
        _nested(value, ("metadata", "gtfs_feed_sha256")),
    ):
        digest = _clean(candidate).lower()
        if digest:
            return validate_sha256(digest, "GTFS Validator feed SHA256")
    return ""


def _nested(value: Mapping[str, Any], keys: Sequence[str]) -> Any:
    current: Any = value
    for key in keys:
        if not isinstance(current, Mapping):
            return None
        current = current.get(key)
    return current


def _int_value(value: object) -> int:
    if value is None or value == "":
        return 0
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"GTFS Validator count must be an integer: {value!r}") from exc
    if parsed < 0:
        raise ValueError(f"GTFS Validator count must be non-negative: {value!r}")
    return parsed


def _first_int_value(value: Mapping[str, Any], *keys: str) -> int:
    for key in keys:
        if key in value:
            return _int_value(value.get(key))
    return 0


def _total_count(value: Mapping[str, Any], errors: int, warnings: int, infos: int) -> int:
    if "total" in value:
        return _int_value(value.get("total"))
    return errors + warnings + infos


__all__ = [
    "REQUIRED_GTFS_FILES",
    "REQUIRED_STOPS_COLUMNS",
    "REQUIRED_STOP_TIMES_COLUMNS",
    "REQUIRED_TRIPS_COLUMNS",
    "CachedGtfsFeed",
    "GtfsEvidenceDerivationConfig",
    "GtfsStop",
    "GtfsStopTime",
    "GtfsTrip",
    "derive_rail_service_evidence_from_gtfs",
    "file_sha256",
    "load_cached_gtfs_feed",
    "summarize_gtfs_validator_report",
    "validate_gtfs_validator_report",
]
