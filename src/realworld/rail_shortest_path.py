"""Derive rail travel-time evidence from cached shortest-path extracts."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from src.realworld.rail_evidence import (
    OPTIONAL_COLUMNS,
    REQUIRED_COLUMNS,
    RailServiceEvidence,
)
from src.realworld.source_artifacts import (
    file_sha256 as _source_file_sha256,
    validate_loaded_source_matches_metadata,
)
from src.realworld.rail_station_binding import RailStationBinding


REQUIRED_SHORTEST_PATH_COLUMNS: tuple[str, ...] = (
    "route_id",
    "access_station_name",
    "access_station_code",
    "egress_station_name",
    "egress_station_code",
    "travel_time_min",
    "distance_km",
    "transfer_count",
    "route_type",
)


@dataclass(frozen=True)
class RailShortestPathRecord:
    """One normalized station-to-station rail shortest-path record."""

    route_id: str
    access_station_name: str
    access_station_code: str
    egress_station_name: str
    egress_station_code: str
    travel_time_min: float
    distance_km: float
    transfer_count: int
    route_type: str


@dataclass(frozen=True)
class CachedShortestPathRecords(Sequence[RailShortestPathRecord]):
    """Shortest-path records with retained source path provenance."""

    source_path: str
    records: tuple[RailShortestPathRecord, ...]

    def __len__(self) -> int:
        return len(self.records)

    def __getitem__(self, index):
        return self.records[index]

    def __iter__(self):
        return iter(self.records)


@dataclass(frozen=True)
class RailShortestPathEvidenceConfig:
    """Metadata needed to write a travel-time evidence row."""

    evidence_id: str
    region_id: str
    access_point: str
    egress_point: str
    source_name: str
    source_url_or_citation: str
    extraction_date: str
    headway_min_proxy: float
    capacity_pax_per_train: float
    service_window: str
    route_type: str = "minimum_time"
    source_artifact_path: str = ""
    source_artifact_sha256: str = ""


def load_cached_shortest_path_records(
    path: str | Path,
) -> CachedShortestPathRecords:
    """Load and validate a cached shortest-path CSV extract."""

    shortest_path = Path(path)
    with shortest_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        _validate_columns(reader.fieldnames, shortest_path)
        records: list[RailShortestPathRecord] = []
        for row in reader:
            if None in row:
                raise ValueError(f"{shortest_path}:{reader.line_num} has too many columns")
            if not any(_clean(value) for value in row.values()):
                continue
            records.append(_record_from_row(row, shortest_path, reader.line_num))
    if not records:
        raise ValueError(f"{shortest_path} must contain at least one shortest-path row")
    return CachedShortestPathRecords(source_path=str(shortest_path), records=tuple(records))


def derive_rail_service_evidence_from_shortest_path(
    records: Sequence[RailShortestPathRecord],
    config: RailShortestPathEvidenceConfig,
    *,
    station_bindings: Sequence[RailStationBinding] | None = None,
) -> RailServiceEvidence:
    """Derive station-to-station travel time from cached shortest-path records."""

    if not records:
        raise ValueError("at least one shortest-path record is required")
    if config.headway_min_proxy <= 0.0:
        raise ValueError("headway_min_proxy must be positive")
    if config.capacity_pax_per_train <= 0.0:
        raise ValueError("capacity_pax_per_train must be positive")
    if not config.source_artifact_path or not config.source_artifact_sha256:
        raise ValueError(
            "source_artifact_path and source_artifact_sha256 are required for "
            "cached shortest-path-derived rail evidence"
        )
    _validate_loaded_shortest_path_source(
        records,
        config.source_artifact_path,
        expected_sha256=config.source_artifact_sha256,
    )

    filtered = [
        record
        for record in records
        if _station_token(record.route_type) == _station_token(config.route_type)
    ]
    if not filtered:
        raise ValueError(f"no shortest-path rows match route_type {config.route_type!r}")
    if station_bindings is not None:
        _validate_shortest_path_station_bindings(
            filtered,
            config,
            station_bindings=station_bindings,
        )

    selected = min(filtered, key=lambda record: (record.travel_time_min, record.transfer_count))
    return RailServiceEvidence(
        evidence_id=config.evidence_id,
        region_id=config.region_id,
        access_point=config.access_point,
        egress_point=config.egress_point,
        access_station_name=selected.access_station_name,
        egress_station_name=selected.egress_station_name,
        source_status="cached_shortest_path_derived",
        source_name=config.source_name,
        source_url_or_citation=config.source_url_or_citation,
        extraction_date=config.extraction_date,
        headway_min=float(config.headway_min_proxy),
        travel_time_min=float(selected.travel_time_min),
        capacity_pax_per_train=float(config.capacity_pax_per_train),
        service_window=config.service_window,
        claim_scope=(
            "cached shortest-path-derived rail travel-time evidence; headway "
            "and capacity remain sensitivity-only; not operational forecast"
        ),
        notes=(
            f"Derived from route_id={selected.route_id}, route_type={selected.route_type}, "
            f"distance_km={_format_number(selected.distance_km)}, "
            f"transfer_count={selected.transfer_count}. "
            f"source_artifact_path={config.source_artifact_path}; "
            f"source_artifact_sha256={config.source_artifact_sha256}."
        ),
        derived_fields="travel_time",
        source_artifact_path=config.source_artifact_path,
        source_artifact_sha256=config.source_artifact_sha256,
    )


def write_rail_shortest_path_evidence(
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
            writer.writerow(_evidence_row(record))
    return output_path


def file_sha256(path: str | Path) -> str:
    """Return the SHA256 digest for a cached source artifact."""

    return _source_file_sha256(path)


def _validate_shortest_path_station_bindings(
    records: Sequence[RailShortestPathRecord],
    config: RailShortestPathEvidenceConfig,
    *,
    station_bindings: Sequence[RailStationBinding],
    ) -> None:
    access_codes = {_station_token(record.access_station_code) for record in records}
    egress_codes = {_station_token(record.egress_station_code) for record in records}
    _validate_codes(
        access_codes,
        point_id=config.access_point,
        station_bindings=station_bindings,
        label="access",
    )
    _validate_codes(
        egress_codes,
        point_id=config.egress_point,
        station_bindings=station_bindings,
        label="egress",
    )


def _validate_loaded_shortest_path_source(
    records: Sequence[RailShortestPathRecord],
    source_artifact_path: str,
    *,
    expected_sha256: str,
) -> None:
    source_path = getattr(records, "source_path", "")
    if source_path:
        validate_loaded_source_matches_metadata(
            source_path,
            source_artifact_path,
            expected_sha256=expected_sha256,
        )
        return
    validate_loaded_source_matches_metadata(
        source_artifact_path,
        source_artifact_path,
        expected_sha256=expected_sha256,
    )


def _validate_codes(
    observed_codes: set[str],
    *,
    point_id: str,
    station_bindings: Sequence[RailStationBinding],
    label: str,
) -> None:
    allowed = _official_station_tokens(station_bindings, point_id=point_id)
    if not allowed:
        raise ValueError(f"no official station binding is available for point {point_id!r}")
    unmatched = sorted(observed_codes - allowed)
    if unmatched:
        raise ValueError(
            f"{label} shortest-path station_code values do not match official "
            f"bindings for point {point_id!r}: {', '.join(unmatched)}; "
            f"allowed={', '.join(sorted(allowed))}"
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


def _validate_columns(fieldnames: Sequence[str] | None, path: Path) -> None:
    if not fieldnames:
        raise ValueError(f"{path} must have a CSV header")
    missing = [column for column in REQUIRED_SHORTEST_PATH_COLUMNS if column not in fieldnames]
    if missing:
        raise ValueError(f"{path} missing required columns: {', '.join(missing)}")


def _record_from_row(
    row: Mapping[str, str | None],
    path: Path,
    line_num: int,
) -> RailShortestPathRecord:
    values = {column: _clean(row.get(column)) for column in REQUIRED_SHORTEST_PATH_COLUMNS}
    for column, value in values.items():
        if not value:
            raise ValueError(f"{path}:{line_num} field {column!r} must be non-empty")
    return RailShortestPathRecord(
        route_id=values["route_id"],
        access_station_name=values["access_station_name"],
        access_station_code=values["access_station_code"],
        egress_station_name=values["egress_station_name"],
        egress_station_code=values["egress_station_code"],
        travel_time_min=_positive_number(values["travel_time_min"], path, line_num),
        distance_km=_positive_number(values["distance_km"], path, line_num),
        transfer_count=_non_negative_int(values["transfer_count"], path, line_num),
        route_type=values["route_type"],
    )


def _evidence_row(record: RailServiceEvidence) -> dict[str, object]:
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
        "gtfs_validator_report_path": record.gtfs_validator_report_path,
        "gtfs_validator_report_sha256": record.gtfs_validator_report_sha256,
    }


def _positive_number(value: str, path: Path, line_num: int) -> float:
    try:
        number = float(value)
    except ValueError as exc:
        raise ValueError(f"{path}:{line_num} expected numeric value for {value!r}") from exc
    if number <= 0.0:
        raise ValueError(f"{path}:{line_num} expected positive value for {value!r}")
    return number


def _non_negative_int(value: str, path: Path, line_num: int) -> int:
    try:
        number = int(value)
    except ValueError as exc:
        raise ValueError(f"{path}:{line_num} expected integer value for {value!r}") from exc
    if number < 0:
        raise ValueError(f"{path}:{line_num} expected non-negative value for {value!r}")
    return number


def _format_number(value: float) -> str:
    if float(value).is_integer():
        return str(int(value))
    return f"{value:.3f}".rstrip("0").rstrip(".")


def _station_token(value: str) -> str:
    return str(value or "").strip().lower()


def _clean(value: object) -> str:
    return "" if value is None else str(value).strip()


__all__ = [
    "REQUIRED_SHORTEST_PATH_COLUMNS",
    "CachedShortestPathRecords",
    "RailShortestPathEvidenceConfig",
    "RailShortestPathRecord",
    "derive_rail_service_evidence_from_shortest_path",
    "file_sha256",
    "load_cached_shortest_path_records",
    "write_rail_shortest_path_evidence",
]
