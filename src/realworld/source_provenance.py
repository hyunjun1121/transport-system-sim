"""Source provenance manifest validation for the quasi-real pilot package.

This module validates a review packet, not an acceptance record. A complete
source provenance manifest makes source URLs, licenses, local artifacts, and
claim boundaries easier to inspect before a reviewer creates
``data/manifests/provenance_acceptance.json``.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE_PROVENANCE_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "source_provenance_manifest.json"
)

REQUIRED_MANIFEST_FIELDS: tuple[str, ...] = (
    "schema_version",
    "region_id",
    "claim_boundary",
    "records",
)
REQUIRED_RECORD_FIELDS: tuple[str, ...] = (
    "source_id",
    "source_name",
    "source_type",
    "source_url_or_citation",
    "license_or_terms",
    "snapshot_or_access_date",
    "local_artifact_paths",
    "used_for",
    "review_status",
    "claim_boundary",
    "notes",
)
ALLOWED_REVIEW_STATUSES: frozenset[str] = frozenset(
    {
        "cached_snapshot_pending_review",
        "context_only_not_cached",
        "repository_input_pending_review",
        "reviewed",
    }
)
ALLOWED_SOURCE_TYPES: frozenset[str] = frozenset(
    {
        "public_map",
        "public_api",
        "public_data",
        "public_router",
        "repository_input",
        "operator_page",
        "agency_news",
    }
)


@dataclass(frozen=True)
class SourceProvenanceRecord:
    """One source-level provenance record."""

    source_id: str
    source_name: str
    source_type: str
    source_url_or_citation: str
    license_or_terms: str
    snapshot_or_access_date: str
    local_artifact_paths: tuple[str, ...]
    used_for: str
    review_status: str
    claim_boundary: str
    notes: str

    @property
    def has_required_text(self) -> bool:
        """Return whether all required text fields are non-empty."""

        return all(
            (
                self.source_id,
                self.source_name,
                self.source_type,
                self.source_url_or_citation,
                self.license_or_terms,
                self.snapshot_or_access_date,
                self.local_artifact_paths,
                self.used_for,
                self.review_status,
                self.claim_boundary,
            )
        )


@dataclass(frozen=True)
class SourceProvenanceManifest:
    """Source provenance review packet for one region."""

    schema_version: int
    region_id: str
    claim_boundary: str
    records: tuple[SourceProvenanceRecord, ...]


def load_source_provenance_manifest(
    path: str | Path = DEFAULT_SOURCE_PROVENANCE_PATH,
) -> SourceProvenanceManifest:
    """Load and validate the source provenance manifest."""

    manifest_path = Path(path)
    with manifest_path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{manifest_path} must contain a JSON object")
    manifest = _manifest_from_mapping(value, manifest_path)
    validate_source_provenance_manifest(manifest, table_name=str(manifest_path))
    return manifest


def summarize_source_provenance_manifest(
    path: str | Path = DEFAULT_SOURCE_PROVENANCE_PATH,
) -> dict[str, Any]:
    """Return conservative diagnostics for the source provenance manifest."""

    manifest_path = Path(path)
    if not manifest_path.exists():
        return {
            "diagnostics_ready": False,
            "path": _display_path(manifest_path),
            "manifest_present": False,
            "record_count": 0,
            "claim_boundary": (
                "Source provenance review packet is absent. This does not "
                "block tests, but it blocks provenance review."
            ),
            "remaining_blockers": ["create source provenance manifest"],
            "review_items": [],
        }

    manifest = load_source_provenance_manifest(manifest_path)
    missing_paths = _missing_local_artifact_paths(manifest.records)
    text_incomplete = [
        record.source_id for record in manifest.records if not record.has_required_text
    ]
    unsupported_statuses = [
        record.source_id
        for record in manifest.records
        if record.review_status not in ALLOWED_REVIEW_STATUSES
    ]
    unsupported_types = [
        record.source_id
        for record in manifest.records
        if record.source_type not in ALLOWED_SOURCE_TYPES
    ]
    blockers: list[str] = []
    if missing_paths:
        blockers.append(
            "source provenance manifest references missing local artifacts: "
            + ", ".join(missing_paths)
        )
    if text_incomplete:
        blockers.append(
            "source provenance records have incomplete required text: "
            + ", ".join(sorted(text_incomplete))
        )
    if unsupported_statuses:
        blockers.append(
            "source provenance records have unsupported review_status values: "
            + ", ".join(sorted(unsupported_statuses))
        )
    if unsupported_types:
        blockers.append(
            "source provenance records have unsupported source_type values: "
            + ", ".join(sorted(unsupported_types))
        )
    if "not operational" not in manifest.claim_boundary.lower():
        blockers.append("source provenance manifest claim_boundary must include 'not operational'")

    status_counts = _status_counts(manifest.records)
    return {
        "diagnostics_ready": not blockers,
        "path": _display_path(manifest_path),
        "manifest_present": True,
        "schema_version": manifest.schema_version,
        "region_id": manifest.region_id,
        "record_count": len(manifest.records),
        "source_type_counts": _source_type_counts(manifest.records),
        "review_status_counts": status_counts,
        "local_artifact_count": len(
            {path for record in manifest.records for path in record.local_artifact_paths}
        ),
        "missing_local_artifact_paths": missing_paths,
        "claim_boundary": manifest.claim_boundary,
        "review_items": _review_items(status_counts),
        "remaining_blockers": blockers,
    }


def validate_source_provenance_manifest(
    manifest: SourceProvenanceManifest,
    *,
    table_name: str = "source provenance manifest",
) -> None:
    """Validate source provenance manifest invariants."""

    if manifest.schema_version < 1:
        raise ValueError(f"{table_name} schema_version must be positive")
    if not manifest.region_id:
        raise ValueError(f"{table_name} region_id must be non-empty")
    if not manifest.claim_boundary:
        raise ValueError(f"{table_name} claim_boundary must be non-empty")
    if not manifest.records:
        raise ValueError(f"{table_name} must contain at least one source record")

    seen: set[str] = set()
    duplicates: set[str] = set()
    for record in manifest.records:
        if record.source_id in seen:
            duplicates.add(record.source_id)
        seen.add(record.source_id)
        _validate_record(record, table_name=table_name)
    if duplicates:
        raise ValueError(
            f"{table_name} has duplicate source_id values: {', '.join(sorted(duplicates))}"
        )


def _validate_record(record: SourceProvenanceRecord, *, table_name: str) -> None:
    if not record.has_required_text:
        raise ValueError(f"{table_name} source record {record.source_id!r} is incomplete")
    if record.source_type not in ALLOWED_SOURCE_TYPES:
        raise ValueError(
            f"{table_name} source record {record.source_id!r} has invalid source_type"
        )
    if record.review_status not in ALLOWED_REVIEW_STATUSES:
        raise ValueError(
            f"{table_name} source record {record.source_id!r} has invalid review_status"
        )


def _manifest_from_mapping(
    value: Mapping[str, Any],
    path: Path,
) -> SourceProvenanceManifest:
    missing = [field for field in REQUIRED_MANIFEST_FIELDS if field not in value]
    if missing:
        raise ValueError(f"{path} missing required fields: {', '.join(missing)}")
    records_value = value["records"]
    if not isinstance(records_value, Sequence) or isinstance(records_value, str):
        raise ValueError(f"{path} records must be a list")
    return SourceProvenanceManifest(
        schema_version=_positive_int(value, "schema_version", path),
        region_id=_clean(value["region_id"]),
        claim_boundary=_clean(value["claim_boundary"]),
        records=tuple(_record_from_mapping(record, path) for record in records_value),
    )


def _record_from_mapping(value: object, path: Path) -> SourceProvenanceRecord:
    if not isinstance(value, Mapping):
        raise ValueError(f"{path} records must contain JSON objects")
    missing = [field for field in REQUIRED_RECORD_FIELDS if field not in value]
    if missing:
        raise ValueError(
            f"{path} source provenance record missing fields: {', '.join(missing)}"
        )
    local_artifact_paths = value["local_artifact_paths"]
    if not isinstance(local_artifact_paths, Sequence) or isinstance(
        local_artifact_paths,
        str,
    ):
        raise ValueError(f"{path} local_artifact_paths must be a list of paths")
    return SourceProvenanceRecord(
        source_id=_clean(value["source_id"]),
        source_name=_clean(value["source_name"]),
        source_type=_clean(value["source_type"]),
        source_url_or_citation=_clean(value["source_url_or_citation"]),
        license_or_terms=_clean(value["license_or_terms"]),
        snapshot_or_access_date=_clean(value["snapshot_or_access_date"]),
        local_artifact_paths=tuple(
            _clean(item) for item in local_artifact_paths if _clean(item)
        ),
        used_for=_clean(value["used_for"]),
        review_status=_clean(value["review_status"]),
        claim_boundary=_clean(value["claim_boundary"]),
        notes=_clean(value["notes"]),
    )


def _positive_int(value: Mapping[str, Any], field: str, path: Path) -> int:
    raw = value[field]
    if isinstance(raw, bool) or not isinstance(raw, int):
        raise ValueError(f"{path} field {field!r} must be an integer")
    if raw < 1:
        raise ValueError(f"{path} field {field!r} must be positive")
    return raw


def _missing_local_artifact_paths(
    records: Sequence[SourceProvenanceRecord],
) -> list[str]:
    missing: list[str] = []
    for record in records:
        for raw_path in record.local_artifact_paths:
            artifact_path = Path(raw_path)
            if not artifact_path.is_absolute():
                artifact_path = PROJECT_ROOT / artifact_path
            if not artifact_path.exists():
                missing.append(raw_path)
    return sorted(set(missing))


def _status_counts(records: Sequence[SourceProvenanceRecord]) -> dict[str, int]:
    counts = {status: 0 for status in sorted(ALLOWED_REVIEW_STATUSES)}
    for record in records:
        counts[record.review_status] = counts.get(record.review_status, 0) + 1
    return {key: value for key, value in counts.items() if value}


def _source_type_counts(records: Sequence[SourceProvenanceRecord]) -> dict[str, int]:
    counts = {source_type: 0 for source_type in sorted(ALLOWED_SOURCE_TYPES)}
    for record in records:
        counts[record.source_type] = counts.get(record.source_type, 0) + 1
    return {key: value for key, value in counts.items() if value}


def _review_items(status_counts: Mapping[str, int]) -> list[str]:
    items: list[str] = []
    if status_counts.get("cached_snapshot_pending_review", 0):
        items.append("review cached source snapshots, dates, licenses, and attribution")
    if status_counts.get("context_only_not_cached", 0):
        items.append(
            "provide reviewed target payloads or exclusion decisions for context-source rows before final claims"
        )
    if status_counts.get("repository_input_pending_review", 0):
        items.append("review repository-defined assumptions and synthetic/privacy handling")
    return items


def _clean(value: object) -> str:
    return "" if value is None else str(value).strip()


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


__all__ = [
    "ALLOWED_REVIEW_STATUSES",
    "ALLOWED_SOURCE_TYPES",
    "DEFAULT_SOURCE_PROVENANCE_PATH",
    "REQUIRED_MANIFEST_FIELDS",
    "REQUIRED_RECORD_FIELDS",
    "SourceProvenanceManifest",
    "SourceProvenanceRecord",
    "load_source_provenance_manifest",
    "summarize_source_provenance_manifest",
    "validate_source_provenance_manifest",
]
