"""Rail evidence cache validation for quasi-real pilot studies.

The rail evidence cache separates public-source availability and documented
assumptions from values that are actually derived from cached timetable or GTFS
data. Passing this validator does not make the current rail input calibrated.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
import hashlib
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from src.realworld.parameters import numeric_tokens


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RAIL_SERVICE_EVIDENCE_PATH = (
    PROJECT_ROOT / "data" / "parameters" / "rail_service_evidence.csv"
)

REQUIRED_COLUMNS: tuple[str, ...] = (
    "evidence_id",
    "region_id",
    "access_point",
    "egress_point",
    "access_station_name",
    "egress_station_name",
    "source_status",
    "source_name",
    "source_url_or_citation",
    "extraction_date",
    "headway_min",
    "travel_time_min",
    "capacity_pax_per_train",
    "service_window",
    "claim_scope",
    "notes",
)
OPTIONAL_COLUMNS: tuple[str, ...] = (
    "derived_fields",
    "source_artifact_path",
    "source_artifact_sha256",
)

ALLOWED_SOURCE_STATUSES: frozenset[str] = frozenset(
    {
        "cached_gtfs_derived",
        "cached_shortest_path_derived",
        "cached_timetable_derived",
        "documented_public_source_available",
        "documented_assumption_proxy",
    }
)
DERIVED_SOURCE_STATUSES: frozenset[str] = frozenset(
    {"cached_gtfs_derived", "cached_shortest_path_derived", "cached_timetable_derived"}
)
ASSUMPTION_SOURCE_STATUSES: frozenset[str] = frozenset(
    {"documented_public_source_available", "documented_assumption_proxy"}
)


@dataclass(frozen=True)
class RailServiceEvidence:
    """One rail evidence-cache row."""

    evidence_id: str
    region_id: str
    access_point: str
    egress_point: str
    access_station_name: str
    egress_station_name: str
    source_status: str
    source_name: str
    source_url_or_citation: str
    extraction_date: str
    headway_min: float
    travel_time_min: float
    capacity_pax_per_train: float
    service_window: str
    claim_scope: str
    notes: str
    derived_fields: str = ""
    source_artifact_path: str = ""
    source_artifact_sha256: str = ""

    @property
    def is_derived(self) -> bool:
        """Return whether values are derived from cached timetable/GTFS data."""

        return self.source_status in DERIVED_SOURCE_STATUSES

    @property
    def derived_field_set(self) -> frozenset[str]:
        """Return normalized rail-service fields derived from cached evidence."""

        if self.derived_fields:
            return frozenset(_field_tokens(self.derived_fields))
        if self.source_status == "cached_timetable_derived":
            return frozenset({"headway", "travel_time"})
        if self.source_status == "cached_shortest_path_derived":
            return frozenset({"travel_time"})
        if self.source_status == "cached_gtfs_derived":
            return frozenset({"headway", "travel_time"})
        return frozenset()


def load_rail_service_evidence(
    path: str | Path = DEFAULT_RAIL_SERVICE_EVIDENCE_PATH,
) -> list[RailServiceEvidence]:
    """Load and validate rail service evidence rows."""

    evidence_path = Path(path)
    with evidence_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        _validate_columns(reader.fieldnames, evidence_path)
        records: list[RailServiceEvidence] = []
        for row in reader:
            if None in row:
                raise ValueError(
                    f"{evidence_path}:{reader.line_num} has too many columns"
                )
            if not any(_clean(value) for value in row.values()):
                continue
            record = _record_from_row(row, evidence_path, reader.line_num)
            _validate_record(record, evidence_path, reader.line_num)
            records.append(record)
    validate_rail_service_evidence(records, table_name=str(evidence_path))
    return records


def validate_rail_service_evidence(
    records: Sequence[RailServiceEvidence],
    *,
    table_name: str = "rail service evidence",
) -> None:
    """Validate table-level invariants."""

    if not records:
        raise ValueError(f"{table_name} must contain at least one row")
    seen: set[str] = set()
    duplicates: set[str] = set()
    for record in records:
        if record.evidence_id in seen:
            duplicates.add(record.evidence_id)
        seen.add(record.evidence_id)
    if duplicates:
        raise ValueError(
            f"{table_name} has duplicate evidence_id rows: "
            f"{', '.join(sorted(duplicates))}"
        )


def summarize_rail_service_evidence(
    records: Sequence[RailServiceEvidence],
) -> dict[str, object]:
    """Return conservative rail-evidence status counts and blockers."""

    derived = [record for record in records if record.is_derived]
    assumption = [
        record for record in records if record.source_status in ASSUMPTION_SOURCE_STATUSES
    ]
    source_artifact_ready = bool(derived) and all(
        _source_artifact_is_ready(record) for record in derived
    )
    derived_field_ready = _derived_field_ready(records)
    timing_ready = (
        source_artifact_ready
        and derived_field_ready["headway"]
        and derived_field_ready["travel_time"]
    )
    capacity_ready = any("capacity" in record.derived_field_set for record in derived)
    capacity_sensitivity_acknowledged = any(
        "sensitivity" in f"{record.claim_scope} {record.notes}".lower()
        for record in records
    )
    return {
        "row_count": len(records),
        "derived_record_count": len(derived),
        "assumption_proxy_count": len(assumption),
        "derived_field_counts": _derived_field_counts(records),
        "derived_field_ready": dict(derived_field_ready),
        "timing_evidence_ready": timing_ready,
        "source_artifact_ready": source_artifact_ready,
        "capacity_evidence_ready": capacity_ready,
        "capacity_sensitivity_acknowledged": capacity_sensitivity_acknowledged,
        "publication_ready": timing_ready
        and source_artifact_ready
        and (capacity_ready or capacity_sensitivity_acknowledged),
        "claim_boundary": (
            "Rail values are publication-ready only when cached evidence "
            "derives both headway and travel time, the source artifact is "
            "committed or otherwise reproducible with a matching SHA256 "
            "digest, and rail capacity is either source-backed or explicitly "
            "retained as a sensitivity-only value."
        ),
        "remaining_blockers": _rail_blockers(records),
    }


def _rail_blockers(records: Sequence[RailServiceEvidence]) -> list[str]:
    derived = [record for record in records if record.is_derived]
    source_artifact_ready = bool(derived) and all(
        _source_artifact_is_ready(record) for record in derived
    )
    derived_field_ready = _derived_field_ready(records)
    timing_ready = (
        source_artifact_ready
        and derived_field_ready["headway"]
        and derived_field_ready["travel_time"]
    )
    capacity_ready = any("capacity" in record.derived_field_set for record in derived)
    capacity_sensitivity_acknowledged = any(
        "sensitivity" in f"{record.claim_scope} {record.notes}".lower()
        for record in records
    )

    blockers: list[str] = []
    if not derived:
        blockers.append("cache timetable, shortest-path, or GTFS-derived records")
    if not (derived_field_ready["headway"] and derived_field_ready["travel_time"]):
        blockers.append("derive headway and travel time from the cached records")
    if derived and not source_artifact_ready:
        blockers.append("record source artifact path and SHA256 for cached rail evidence")
    if not (capacity_ready or capacity_sensitivity_acknowledged):
        blockers.append(
            "replace capacity proxy or keep it as an explicit sensitivity-only value"
        )
    return blockers


def _validate_columns(fieldnames: Sequence[str] | None, path: Path) -> None:
    if not fieldnames:
        raise ValueError(f"{path} must have a CSV header")
    missing = [column for column in REQUIRED_COLUMNS if column not in fieldnames]
    if missing:
        raise ValueError(f"{path} missing required columns: {', '.join(missing)}")


def _record_from_row(
    row: Mapping[str, str | None],
    path: Path,
    line_num: int,
) -> RailServiceEvidence:
    values = {column: _clean(row.get(column)) for column in REQUIRED_COLUMNS}
    optional_values = {column: _clean(row.get(column)) for column in OPTIONAL_COLUMNS}
    for column, value in values.items():
        if not value:
            raise ValueError(f"{path}:{line_num} field {column!r} must be non-empty")
    return RailServiceEvidence(
        evidence_id=values["evidence_id"],
        region_id=values["region_id"],
        access_point=values["access_point"],
        egress_point=values["egress_point"],
        access_station_name=values["access_station_name"],
        egress_station_name=values["egress_station_name"],
        source_status=values["source_status"],
        source_name=values["source_name"],
        source_url_or_citation=values["source_url_or_citation"],
        extraction_date=values["extraction_date"],
        headway_min=_positive_number(values["headway_min"], path, line_num),
        travel_time_min=_positive_number(values["travel_time_min"], path, line_num),
        capacity_pax_per_train=_positive_number(
            values["capacity_pax_per_train"],
            path,
            line_num,
        ),
        service_window=values["service_window"],
        claim_scope=values["claim_scope"],
        notes=values["notes"],
        derived_fields=optional_values["derived_fields"],
        source_artifact_path=optional_values["source_artifact_path"],
        source_artifact_sha256=optional_values["source_artifact_sha256"],
    )


def _validate_record(record: RailServiceEvidence, path: Path, line_num: int) -> None:
    location = f"{path}:{line_num}"
    if record.source_status not in ALLOWED_SOURCE_STATUSES:
        allowed = ", ".join(sorted(ALLOWED_SOURCE_STATUSES))
        raise ValueError(
            f"{location} has invalid source_status {record.source_status!r}; "
            f"allowed: {allowed}"
        )
    claim_scope = record.claim_scope.lower()
    if record.source_status in ASSUMPTION_SOURCE_STATUSES:
        if "not calibrated" not in claim_scope:
            raise ValueError(
                f"{location} assumption rail row must include 'not calibrated' "
                "in claim_scope"
            )
    if record.is_derived and "cached" not in record.source_status:
        raise ValueError(f"{location} derived rail row must be cached")
    for field in record.derived_field_set:
        if field not in {"headway", "travel_time", "capacity"}:
            raise ValueError(f"{location} has invalid derived field {field!r}")
    if record.is_derived and not record.source_artifact_path:
        raise ValueError(f"{location} derived rail row must include source_artifact_path")
    if record.is_derived and not record.source_artifact_sha256:
        raise ValueError(
            f"{location} derived rail row must include source_artifact_sha256"
        )
    if record.source_artifact_sha256 and not _is_sha256(record.source_artifact_sha256):
        raise ValueError(f"{location} source_artifact_sha256 must be 64 hex characters")


def _positive_number(value: str, path: Path, line_num: int) -> float:
    numbers = numeric_tokens(value)
    if not numbers:
        raise ValueError(f"{path}:{line_num} expected numeric value, got {value!r}")
    number = float(numbers[0])
    if number <= 0.0:
        raise ValueError(f"{path}:{line_num} expected positive value, got {value!r}")
    return number


def _clean(value: object) -> str:
    return "" if value is None else str(value).strip()


def _field_tokens(value: str) -> list[str]:
    normalized = str(value).replace(",", ";").replace("|", ";")
    return [
        token.strip().lower()
        for token in normalized.split(";")
        if token.strip()
    ]


def _derived_field_counts(
    records: Sequence[RailServiceEvidence],
) -> dict[str, int]:
    counts = {"headway": 0, "travel_time": 0, "capacity": 0}
    for record in records:
        for field in record.derived_field_set:
            if field in counts:
                counts[field] += 1
    return counts


def _derived_field_ready(
    records: Sequence[RailServiceEvidence],
) -> dict[str, bool]:
    counts = _derived_field_counts(records)
    return {
        "headway": counts["headway"] > 0,
        "travel_time": counts["travel_time"] > 0,
        "capacity": counts["capacity"] > 0,
    }


def _is_sha256(value: str) -> bool:
    return len(value) == 64 and all(
        character in "0123456789abcdefABCDEF" for character in value
    )


def _source_artifact_is_ready(record: RailServiceEvidence) -> bool:
    if not record.source_artifact_path or not record.source_artifact_sha256:
        return False
    if not _is_sha256(record.source_artifact_sha256):
        return False
    artifact_path = Path(record.source_artifact_path)
    if not artifact_path.is_absolute():
        artifact_path = PROJECT_ROOT / artifact_path
    if not artifact_path.exists() or not artifact_path.is_file():
        return False
    return _file_sha256(artifact_path).lower() == record.source_artifact_sha256.lower()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


__all__ = [
    "ALLOWED_SOURCE_STATUSES",
    "ASSUMPTION_SOURCE_STATUSES",
    "DEFAULT_RAIL_SERVICE_EVIDENCE_PATH",
    "DERIVED_SOURCE_STATUSES",
    "OPTIONAL_COLUMNS",
    "REQUIRED_COLUMNS",
    "RailServiceEvidence",
    "load_rail_service_evidence",
    "summarize_rail_service_evidence",
    "validate_rail_service_evidence",
]
