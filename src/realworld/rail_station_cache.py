"""Derive official station bindings from reviewed cached station extracts."""

from __future__ import annotations

import csv
from dataclasses import dataclass
import hashlib
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from src.realworld.rail_station_binding import (
    RailStationBinding,
    write_rail_station_bindings,
)


REQUIRED_STATION_CACHE_COLUMNS: tuple[str, ...] = (
    "point_id",
    "station_name",
    "station_id",
    "station_code",
    "line",
)

PLACEHOLDER_VALUES: frozenset[str] = frozenset(
    {"", "-", "na", "n/a", "none", "null", "pending", "tbd", "unknown"}
)


@dataclass(frozen=True)
class CachedStationBindingCandidate:
    """One cached source row that maps a simulator rail point to a station."""

    point_id: str
    station_name: str
    station_id: str
    station_code: str
    line: str


@dataclass(frozen=True)
class StationBindingDerivationConfig:
    """Metadata needed to write official station-binding evidence rows."""

    binding_id_prefix: str
    region_id: str
    source_name: str
    source_url_or_citation: str
    source_accessed_date: str
    source_artifact_path: str = ""
    source_artifact_sha256: str = ""


def load_cached_station_binding_candidates(
    path: str | Path,
) -> list[CachedStationBindingCandidate]:
    """Load a reviewed station-binding candidate CSV."""

    cache_path = Path(path)
    with cache_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        _validate_columns(reader.fieldnames, cache_path)
        records: list[CachedStationBindingCandidate] = []
        for row in reader:
            if None in row:
                raise ValueError(f"{cache_path}:{reader.line_num} has too many columns")
            if not any(_clean(value) for value in row.values()):
                continue
            record = _candidate_from_row(row, cache_path, reader.line_num)
            _validate_candidate(record, cache_path, reader.line_num)
            records.append(record)
    if not records:
        raise ValueError(f"{cache_path} must contain at least one station row")
    _validate_unique_candidates(records, table_name=str(cache_path))
    return records


def derive_rail_station_bindings_from_cache(
    candidates: Sequence[CachedStationBindingCandidate],
    config: StationBindingDerivationConfig,
) -> list[RailStationBinding]:
    """Convert cached station rows into official station-binding records."""

    if not candidates:
        raise ValueError("at least one station-binding candidate is required")
    if not _clean(config.binding_id_prefix):
        raise ValueError("binding_id_prefix must be non-empty")
    if not _clean(config.region_id):
        raise ValueError("region_id must be non-empty")

    records: list[RailStationBinding] = []
    for candidate in candidates:
        identifier = (
            candidate.station_code
            if not _is_placeholder(candidate.station_code)
            else candidate.station_id
        )
        records.append(
            RailStationBinding(
                binding_id=(
                    f"{config.binding_id_prefix}_{candidate.point_id}_"
                    f"{_candidate_suffix(candidate)}"
                ),
                region_id=config.region_id,
                point_id=candidate.point_id,
                station_name=candidate.station_name,
                station_id=candidate.station_id,
                station_code=candidate.station_code,
                source_name=config.source_name,
                source_url_or_citation=config.source_url_or_citation,
                source_accessed_date=config.source_accessed_date,
                source_status="official_station_code_bound",
                claim_scope=(
                    "official station-code binding from cached station source; "
                    "not operational rail service evidence"
                ),
                notes=(
                    f"Bound {candidate.point_id} to {candidate.station_name} "
                    f"on {candidate.line} using identifier {identifier}."
                    f"{_artifact_note(config)}"
                ),
            )
        )
    return records


def write_derived_rail_station_bindings(
    records: Iterable[RailStationBinding],
    path: str | Path,
) -> Path:
    """Write derived station bindings to the repository binding schema."""

    return write_rail_station_bindings(records, path)


def file_sha256(path: str | Path) -> str:
    """Return the SHA256 digest for a cached source artifact."""

    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _candidate_from_row(
    row: Mapping[str, str | None],
    path: Path,
    line_num: int,
) -> CachedStationBindingCandidate:
    values = {column: _clean(row.get(column)) for column in REQUIRED_STATION_CACHE_COLUMNS}
    for column, value in values.items():
        if not value:
            raise ValueError(f"{path}:{line_num} field {column!r} must be non-empty")
    return CachedStationBindingCandidate(
        point_id=values["point_id"],
        station_name=values["station_name"],
        station_id=values["station_id"],
        station_code=values["station_code"],
        line=values["line"],
    )


def _validate_candidate(
    record: CachedStationBindingCandidate,
    path: Path,
    line_num: int,
) -> None:
    if _is_placeholder(record.station_id) and _is_placeholder(record.station_code):
        raise ValueError(
            f"{path}:{line_num} official station candidate requires station_id "
            "or station_code"
        )


def _validate_unique_candidates(
    records: Sequence[CachedStationBindingCandidate],
    *,
    table_name: str,
) -> None:
    seen: set[tuple[str, str, str, str]] = set()
    duplicates: set[tuple[str, str, str, str]] = set()
    for record in records:
        key = (
            record.point_id,
            record.station_id,
            record.station_code,
            record.line,
        )
        if key in seen:
            duplicates.add(key)
        seen.add(key)
    if duplicates:
        labels = [
            f"{point_id}/{station_id}/{station_code}/{line}"
            for point_id, station_id, station_code, line in sorted(duplicates)
        ]
        raise ValueError(
            f"{table_name} has duplicate station candidate rows: "
            f"{', '.join(labels)}"
        )


def _validate_columns(fieldnames: Sequence[str] | None, path: Path) -> None:
    if not fieldnames:
        raise ValueError(f"{path} must have a CSV header")
    missing = [
        column for column in REQUIRED_STATION_CACHE_COLUMNS if column not in fieldnames
    ]
    if missing:
        raise ValueError(f"{path} missing required columns: {', '.join(missing)}")


def _artifact_note(config: StationBindingDerivationConfig) -> str:
    parts: list[str] = []
    if config.source_artifact_path:
        parts.append(f"source_artifact_path={config.source_artifact_path}")
    if config.source_artifact_sha256:
        parts.append(f"source_artifact_sha256={config.source_artifact_sha256}")
    if not parts:
        return ""
    return " " + "; ".join(parts) + "."


def _candidate_suffix(candidate: CachedStationBindingCandidate) -> str:
    identifier = (
        candidate.station_code
        if not _is_placeholder(candidate.station_code)
        else candidate.station_id
    )
    return _safe_identifier(f"{candidate.line}_{identifier}")


def _safe_identifier(value: str) -> str:
    cleaned = []
    for character in value.strip().lower():
        if character.isascii() and character.isalnum():
            cleaned.append(character)
        else:
            cleaned.append("_")
    compact = "_".join(part for part in "".join(cleaned).split("_") if part)
    return compact or "station"


def _is_placeholder(value: str) -> bool:
    return value.strip().lower() in PLACEHOLDER_VALUES


def _clean(value: object) -> str:
    return "" if value is None else str(value).strip()


__all__ = [
    "CachedStationBindingCandidate",
    "REQUIRED_STATION_CACHE_COLUMNS",
    "StationBindingDerivationConfig",
    "derive_rail_station_bindings_from_cache",
    "file_sha256",
    "load_cached_station_binding_candidates",
    "write_derived_rail_station_bindings",
]
