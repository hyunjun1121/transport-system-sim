"""Derive rail service evidence from cached timetable extracts.

The default project must not call live transit APIs. This module therefore
expects a committed or locally reviewed CSV extract and converts it into the
existing rail-service evidence schema.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
import hashlib
from pathlib import Path
from statistics import median
from typing import Iterable, Mapping, Sequence

from src.realworld.rail_evidence import (
    OPTIONAL_COLUMNS,
    REQUIRED_COLUMNS,
    RailServiceEvidence,
)
from src.realworld.rail_station_binding import RailStationBinding


REQUIRED_TIMETABLE_COLUMNS: tuple[str, ...] = (
    "trip_id",
    "station_role",
    "station_name",
    "station_code",
    "event_time",
    "event_type",
    "direction",
    "service_day",
)

ALLOWED_STATION_ROLES: frozenset[str] = frozenset({"access", "egress"})
ALLOWED_EVENT_TYPES: frozenset[str] = frozenset({"departure", "arrival"})


@dataclass(frozen=True)
class RailTimetableEvent:
    """One normalized station event from a cached timetable extract."""

    trip_id: str
    station_role: str
    station_name: str
    station_code: str
    event_time_min: float
    event_type: str
    direction: str
    service_day: str


@dataclass(frozen=True)
class RailEvidenceDerivationConfig:
    """Metadata needed to write one rail-service evidence row."""

    evidence_id: str
    region_id: str
    access_point: str
    egress_point: str
    source_name: str
    source_url_or_citation: str
    extraction_date: str
    capacity_pax_per_train: float
    service_window: str
    direction: str = ""
    service_day: str = ""
    source_artifact_path: str = ""
    source_artifact_sha256: str = ""


@dataclass(frozen=True)
class RailHeadwayEvidenceConfig:
    """Metadata for a timetable row that derives headway only."""

    evidence_id: str
    region_id: str
    access_point: str
    egress_point: str
    egress_station_name: str
    source_name: str
    source_url_or_citation: str
    extraction_date: str
    travel_time_min_proxy: float
    capacity_pax_per_train: float
    service_window: str
    direction: str = ""
    service_day: str = ""
    source_artifact_path: str = ""
    source_artifact_sha256: str = ""


def load_cached_timetable_events(path: str | Path) -> list[RailTimetableEvent]:
    """Load and validate a cached station-event timetable CSV."""

    timetable_path = Path(path)
    with timetable_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        _validate_columns(reader.fieldnames, timetable_path)
        events: list[RailTimetableEvent] = []
        for row in reader:
            if None in row:
                raise ValueError(f"{timetable_path}:{reader.line_num} has too many columns")
            if not any(_clean(value) for value in row.values()):
                continue
            events.append(_event_from_row(row, timetable_path, reader.line_num))
    if not events:
        raise ValueError(f"{timetable_path} must contain at least one timetable event")
    return events


def derive_rail_service_evidence_from_timetable(
    events: Sequence[RailTimetableEvent],
    config: RailEvidenceDerivationConfig,
    *,
    station_bindings: Sequence[RailStationBinding] | None = None,
) -> RailServiceEvidence:
    """Derive headway and travel time from cached access/egress station events."""

    if not events:
        raise ValueError("at least one timetable event is required")
    if config.capacity_pax_per_train <= 0.0:
        raise ValueError("capacity_pax_per_train must be positive")
    if not config.source_artifact_path or not config.source_artifact_sha256:
        raise ValueError(
            "source_artifact_path and source_artifact_sha256 are required for "
            "cached timetable-derived rail evidence"
        )

    filtered = _filter_events(
        events,
        direction=config.direction,
        service_day=config.service_day,
    )
    if station_bindings is not None:
        validate_timetable_station_bindings(
            filtered,
            config,
            station_bindings=station_bindings,
        )
    access_departures = sorted(
        (
            event
            for event in filtered
            if event.station_role == "access" and event.event_type == "departure"
        ),
        key=lambda event: event.event_time_min,
    )
    if len(access_departures) < 2:
        raise ValueError("at least two access departures are required to derive headway")

    matched_travel_times = _matched_travel_times(filtered)
    if not matched_travel_times:
        raise ValueError("at least one matched access-departure to egress-arrival trip is required")

    headways = [
        access_departures[index + 1].event_time_min - access_departures[index].event_time_min
        for index in range(len(access_departures) - 1)
    ]
    if any(headway <= 0.0 for headway in headways):
        raise ValueError("access departures must be strictly increasing for the selected filter")

    access_station_name = access_departures[0].station_name
    egress_arrivals = [
        event
        for event in filtered
        if event.station_role == "egress" and event.event_type == "arrival"
    ]
    if not egress_arrivals:
        raise ValueError("at least one egress arrival is required")

    return RailServiceEvidence(
        evidence_id=config.evidence_id,
        region_id=config.region_id,
        access_point=config.access_point,
        egress_point=config.egress_point,
        access_station_name=access_station_name,
        egress_station_name=egress_arrivals[0].station_name,
        source_status="cached_timetable_derived",
        source_name=config.source_name,
        source_url_or_citation=config.source_url_or_citation,
        extraction_date=config.extraction_date,
        headway_min=float(median(headways)),
        travel_time_min=float(median(matched_travel_times)),
        capacity_pax_per_train=float(config.capacity_pax_per_train),
        service_window=config.service_window,
        claim_scope=(
            "cached timetable-derived rail timing evidence; capacity remains "
            "sensitivity-only; not operational forecast"
        ),
        notes=(
            f"Derived from {len(access_departures)} access departures and "
            f"{len(matched_travel_times)} matched station-to-station trips."
            f"{_artifact_note(config)}"
        ),
        derived_fields="headway;travel_time",
        source_artifact_path=config.source_artifact_path,
        source_artifact_sha256=config.source_artifact_sha256,
    )


def derive_rail_headway_evidence_from_timetable(
    events: Sequence[RailTimetableEvent],
    config: RailHeadwayEvidenceConfig,
    *,
    station_bindings: Sequence[RailStationBinding] | None = None,
) -> RailServiceEvidence:
    """Derive access-station headway from cached station-event timetable rows.

    Travel time is carried as a positive proxy because the repository evidence
    schema stores one rail-service row shape. The row explicitly declares
    ``derived_fields=headway`` so it cannot satisfy the travel-time evidence
    gate by itself.
    """

    if not events:
        raise ValueError("at least one timetable event is required")
    if config.travel_time_min_proxy <= 0.0:
        raise ValueError("travel_time_min_proxy must be positive")
    if config.capacity_pax_per_train <= 0.0:
        raise ValueError("capacity_pax_per_train must be positive")
    if not config.source_artifact_path or not config.source_artifact_sha256:
        raise ValueError(
            "source_artifact_path and source_artifact_sha256 are required for "
            "cached timetable-derived headway evidence"
        )

    filtered = _filter_events(
        events,
        direction=config.direction,
        service_day=config.service_day,
    )
    if station_bindings is not None:
        _validate_role_station_binding(
            filtered,
            role="access",
            point_id=config.access_point,
            station_bindings=station_bindings,
        )
    access_departures = sorted(
        (
            event
            for event in filtered
            if event.station_role == "access" and event.event_type == "departure"
        ),
        key=lambda event: event.event_time_min,
    )
    if len(access_departures) < 2:
        raise ValueError("at least two access departures are required to derive headway")

    headways = [
        access_departures[index + 1].event_time_min - access_departures[index].event_time_min
        for index in range(len(access_departures) - 1)
    ]
    if any(headway <= 0.0 for headway in headways):
        raise ValueError("access departures must be strictly increasing for the selected filter")

    return RailServiceEvidence(
        evidence_id=config.evidence_id,
        region_id=config.region_id,
        access_point=config.access_point,
        egress_point=config.egress_point,
        access_station_name=access_departures[0].station_name,
        egress_station_name=config.egress_station_name,
        source_status="cached_timetable_derived",
        source_name=config.source_name,
        source_url_or_citation=config.source_url_or_citation,
        extraction_date=config.extraction_date,
        headway_min=float(median(headways)),
        travel_time_min=float(config.travel_time_min_proxy),
        capacity_pax_per_train=float(config.capacity_pax_per_train),
        service_window=config.service_window,
        claim_scope=(
            "cached timetable-derived rail headway evidence; travel time and "
            "capacity remain separate assumptions or sensitivity-only values; "
            "not operational forecast"
        ),
        notes=(
            f"Derived headway from {len(access_departures)} access departures. "
            "travel_time_min is a carried proxy and is not a derived field."
            f"{_artifact_note(config)}"
        ),
        derived_fields="headway",
        source_artifact_path=config.source_artifact_path,
        source_artifact_sha256=config.source_artifact_sha256,
    )


def write_rail_service_evidence(
    records: Iterable[RailServiceEvidence],
    path: str | Path,
) -> Path:
    """Write rail-service evidence records using the repository schema."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REQUIRED_COLUMNS + OPTIONAL_COLUMNS)
        writer.writeheader()
        for record in records:
            writer.writerow(_record_to_row(record))
    return output_path


def validate_timetable_station_bindings(
    events: Sequence[RailTimetableEvent],
    config: RailEvidenceDerivationConfig,
    *,
    station_bindings: Sequence[RailStationBinding],
) -> None:
    """Ensure cached timetable station codes match official rail-point bindings."""

    if not station_bindings:
        raise ValueError("station_bindings must contain official station rows")
    _validate_role_station_binding(
        events,
        role="access",
        point_id=config.access_point,
        station_bindings=station_bindings,
    )
    _validate_role_station_binding(
        events,
        role="egress",
        point_id=config.egress_point,
        station_bindings=station_bindings,
    )


def parse_service_time_min(value: str) -> float:
    """Parse HH:MM or HH:MM:SS service time, including GTFS-style hours >= 24."""

    parts = [part.strip() for part in str(value).strip().split(":")]
    if len(parts) not in (2, 3):
        raise ValueError(f"invalid service time {value!r}; expected HH:MM or HH:MM:SS")
    try:
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = int(parts[2]) if len(parts) == 3 else 0
    except ValueError as exc:
        raise ValueError(f"invalid service time {value!r}") from exc
    if hours < 0 or not 0 <= minutes < 60 or not 0 <= seconds < 60:
        raise ValueError(f"invalid service time {value!r}")
    return hours * 60.0 + minutes + seconds / 60.0


def file_sha256(path: str | Path) -> str:
    """Return the SHA256 digest for a cached source artifact."""

    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _validate_columns(fieldnames: Sequence[str] | None, path: Path) -> None:
    if not fieldnames:
        raise ValueError(f"{path} must have a CSV header")
    missing = [column for column in REQUIRED_TIMETABLE_COLUMNS if column not in fieldnames]
    if missing:
        raise ValueError(f"{path} missing required columns: {', '.join(missing)}")


def _event_from_row(
    row: Mapping[str, str | None],
    path: Path,
    line_num: int,
) -> RailTimetableEvent:
    values = {column: _clean(row.get(column)) for column in REQUIRED_TIMETABLE_COLUMNS}
    for column, value in values.items():
        if not value:
            raise ValueError(f"{path}:{line_num} field {column!r} must be non-empty")

    station_role = values["station_role"].lower()
    if station_role not in ALLOWED_STATION_ROLES:
        raise ValueError(f"{path}:{line_num} has invalid station_role {station_role!r}")
    event_type = values["event_type"].lower()
    if event_type not in ALLOWED_EVENT_TYPES:
        raise ValueError(f"{path}:{line_num} has invalid event_type {event_type!r}")

    return RailTimetableEvent(
        trip_id=values["trip_id"],
        station_role=station_role,
        station_name=values["station_name"],
        station_code=values["station_code"],
        event_time_min=parse_service_time_min(values["event_time"]),
        event_type=event_type,
        direction=values["direction"],
        service_day=values["service_day"],
    )


def _filter_events(
    events: Sequence[RailTimetableEvent],
    *,
    direction: str,
    service_day: str,
) -> list[RailTimetableEvent]:
    return [
        event
        for event in events
        if (not direction or event.direction == direction)
        and (not service_day or event.service_day == service_day)
    ]


def _matched_travel_times(events: Sequence[RailTimetableEvent]) -> list[float]:
    by_trip: dict[str, dict[str, RailTimetableEvent]] = {}
    for event in events:
        by_trip.setdefault(event.trip_id, {})[f"{event.station_role}:{event.event_type}"] = event

    travel_times: list[float] = []
    for trip_events in by_trip.values():
        access = trip_events.get("access:departure")
        egress = trip_events.get("egress:arrival")
        if access is None or egress is None:
            continue
        travel_time = egress.event_time_min - access.event_time_min
        if travel_time < 0.0:
            travel_time += 24.0 * 60.0
        if travel_time <= 0.0:
            raise ValueError("matched access-to-egress travel time must be positive")
        travel_times.append(travel_time)
    return travel_times


def _validate_role_station_binding(
    events: Sequence[RailTimetableEvent],
    *,
    role: str,
    point_id: str,
    station_bindings: Sequence[RailStationBinding],
) -> None:
    role_events = [event for event in events if event.station_role == role]
    if not role_events:
        raise ValueError(f"no {role} timetable events are available for binding check")

    allowed_codes = _official_station_tokens(station_bindings, point_id=point_id)
    if not allowed_codes:
        raise ValueError(f"no official station binding is available for point {point_id!r}")

    observed_codes = {_station_token(event.station_code) for event in role_events}
    unmatched = sorted(observed_codes - allowed_codes)
    if unmatched:
        allowed = ", ".join(sorted(allowed_codes))
        raise ValueError(
            f"{role} timetable station_code values do not match official "
            f"bindings for point {point_id!r}: {', '.join(unmatched)}; "
            f"allowed={allowed}"
        )


def _official_station_tokens(
    station_bindings: Sequence[RailStationBinding],
    *,
    point_id: str,
) -> set[str]:
    tokens: set[str] = set()
    for binding in station_bindings:
        if binding.point_id != point_id or not binding.is_official:
            continue
        tokens.add(_station_token(binding.station_code))
        tokens.add(_station_token(binding.station_id))
    return {token for token in tokens if token}


def _station_token(value: str) -> str:
    return str(value or "").strip().lower()


def _record_to_row(record: RailServiceEvidence) -> dict[str, object]:
    return {
        "evidence_id": record.evidence_id,
        "region_id": record.region_id,
        "access_point": record.access_point,
        "egress_point": record.egress_point,
        "access_station_name": record.access_station_name,
        "egress_station_name": record.egress_station_name,
        "source_status": record.source_status,
        "source_name": record.source_name,
        "source_url_or_citation": record.source_url_or_citation,
        "extraction_date": record.extraction_date,
        "headway_min": _format_number(record.headway_min),
        "travel_time_min": _format_number(record.travel_time_min),
        "capacity_pax_per_train": _format_number(record.capacity_pax_per_train),
        "service_window": record.service_window,
        "claim_scope": record.claim_scope,
        "notes": record.notes,
        "derived_fields": record.derived_fields,
        "source_artifact_path": record.source_artifact_path,
        "source_artifact_sha256": record.source_artifact_sha256,
    }


def _format_number(value: float) -> str:
    if float(value).is_integer():
        return str(int(value))
    return f"{value:.3f}".rstrip("0").rstrip(".")


def _artifact_note(config: RailEvidenceDerivationConfig) -> str:
    parts: list[str] = []
    if config.source_artifact_path:
        parts.append(f"source_artifact_path={config.source_artifact_path}")
    if config.source_artifact_sha256:
        parts.append(f"source_artifact_sha256={config.source_artifact_sha256}")
    if not parts:
        return ""
    return " " + "; ".join(parts) + "."


def _clean(value: object) -> str:
    return "" if value is None else str(value).strip()


__all__ = [
    "ALLOWED_EVENT_TYPES",
    "ALLOWED_STATION_ROLES",
    "REQUIRED_TIMETABLE_COLUMNS",
    "RailEvidenceDerivationConfig",
    "RailHeadwayEvidenceConfig",
    "RailTimetableEvent",
    "derive_rail_headway_evidence_from_timetable",
    "derive_rail_service_evidence_from_timetable",
    "file_sha256",
    "load_cached_timetable_events",
    "parse_service_time_min",
    "validate_timetable_station_bindings",
    "write_rail_service_evidence",
]
