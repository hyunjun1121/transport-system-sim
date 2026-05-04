"""Derive rail-service evidence from cached static GTFS feeds.

This module reads a reviewed GTFS zip or directory without live API calls and
converts selected stop-to-stop trips into the repository rail evidence schema.
It is intentionally small: it derives headway and scheduled in-vehicle travel
time only, while capacity remains a supplied sensitivity or reviewed value.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
import hashlib
from io import TextIOWrapper
from pathlib import Path
from statistics import median
from typing import Iterable, Mapping, Sequence
import zipfile

from src.realworld.rail_evidence import RailServiceEvidence
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
            f"source_artifact_sha256={config.source_artifact_sha256}."
        ),
        derived_fields="headway;travel_time",
        source_artifact_path=config.source_artifact_path,
        source_artifact_sha256=config.source_artifact_sha256,
    )


def file_sha256(path: str | Path) -> str:
    """Return the SHA256 digest for a cached GTFS artifact file."""

    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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
]
