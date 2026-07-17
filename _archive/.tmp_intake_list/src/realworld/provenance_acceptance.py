"""Data provenance acceptance record validation.

Final-study data provenance requires more than a reproducibility manifest. This
module validates the explicit review record for source snapshots, licenses,
privacy abstraction, cache manifests, and claim boundaries.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROVENANCE_ACCEPTANCE_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "provenance_acceptance.json"
)

REQUIRED_PROVENANCE_ACCEPTANCE_FIELDS: tuple[str, ...] = (
    "region_id",
    "accepted",
    "accepted_by",
    "accepted_date",
    "source_snapshot_reviewed",
    "license_attribution_reviewed",
    "privacy_abstraction_reviewed",
    "cache_manifest_reviewed",
    "reproducibility_manifest_reviewed",
    "source_urls_or_citations",
    "data_snapshot_paths",
    "evidence_paths",
    "claim_boundary",
)


@dataclass(frozen=True)
class ProvenanceAcceptance:
    """One explicit data-provenance acceptance record."""

    region_id: str
    accepted: bool
    accepted_by: str
    accepted_date: str
    source_snapshot_reviewed: bool
    license_attribution_reviewed: bool
    privacy_abstraction_reviewed: bool
    cache_manifest_reviewed: bool
    reproducibility_manifest_reviewed: bool
    source_urls_or_citations: tuple[str, ...]
    data_snapshot_paths: tuple[str, ...]
    evidence_paths: tuple[str, ...]
    claim_boundary: str

    @property
    def ready(self) -> bool:
        """Return whether this record can satisfy provenance acceptance."""

        return (
            self.accepted
            and bool(self.region_id)
            and bool(self.accepted_by)
            and bool(self.accepted_date)
            and self.source_snapshot_reviewed
            and self.license_attribution_reviewed
            and self.privacy_abstraction_reviewed
            and self.cache_manifest_reviewed
            and self.reproducibility_manifest_reviewed
            and bool(self.source_urls_or_citations)
            and bool(self.data_snapshot_paths)
            and bool(self.evidence_paths)
            and "not operational" in self.claim_boundary.lower()
        )


def load_provenance_acceptance(
    path: str | Path = DEFAULT_PROVENANCE_ACCEPTANCE_PATH,
) -> ProvenanceAcceptance:
    """Load and validate a data-provenance acceptance JSON record."""

    acceptance_path = Path(path)
    with acceptance_path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{acceptance_path} must contain a JSON object")
    record = _acceptance_from_mapping(value, acceptance_path)
    validate_provenance_acceptance(record, table_name=str(acceptance_path))
    return record


def summarize_provenance_acceptance(
    path: str | Path = DEFAULT_PROVENANCE_ACCEPTANCE_PATH,
) -> dict[str, Any]:
    """Return conservative data-provenance acceptance readiness."""

    acceptance_path = Path(path)
    if not acceptance_path.exists():
        return {
            "acceptance_ready": False,
            "path": _display_path(acceptance_path),
            "record_present": False,
            "remaining_blockers": [
                "create an explicit provenance acceptance record after source, license, snapshot, privacy, and reproducibility review"
            ],
        }

    record = load_provenance_acceptance(acceptance_path)
    blockers: list[str] = []
    if not record.accepted:
        blockers.append("provenance acceptance record does not set accepted: true")
    if not record.source_snapshot_reviewed:
        blockers.append("provenance acceptance requires source_snapshot_reviewed: true")
    if not record.license_attribution_reviewed:
        blockers.append(
            "provenance acceptance requires license_attribution_reviewed: true"
        )
    if not record.privacy_abstraction_reviewed:
        blockers.append(
            "provenance acceptance requires privacy_abstraction_reviewed: true"
        )
    if not record.cache_manifest_reviewed:
        blockers.append("provenance acceptance requires cache_manifest_reviewed: true")
    if not record.reproducibility_manifest_reviewed:
        blockers.append(
            "provenance acceptance requires reproducibility_manifest_reviewed: true"
        )
    if not record.source_urls_or_citations:
        blockers.append("provenance acceptance requires source_urls_or_citations")
    if not record.data_snapshot_paths:
        blockers.append("provenance acceptance requires data_snapshot_paths")
    if not record.evidence_paths:
        blockers.append("provenance acceptance requires evidence_paths")
    if "not operational" not in record.claim_boundary.lower():
        blockers.append("provenance acceptance claim_boundary must include 'not operational'")

    return {
        "acceptance_ready": not blockers,
        "path": _display_path(acceptance_path),
        "record_present": True,
        "region_id": record.region_id,
        "source_snapshot_reviewed": record.source_snapshot_reviewed,
        "license_attribution_reviewed": record.license_attribution_reviewed,
        "privacy_abstraction_reviewed": record.privacy_abstraction_reviewed,
        "cache_manifest_reviewed": record.cache_manifest_reviewed,
        "reproducibility_manifest_reviewed": (
            record.reproducibility_manifest_reviewed
        ),
        "source_urls_or_citations": list(record.source_urls_or_citations),
        "data_snapshot_paths": list(record.data_snapshot_paths),
        "evidence_paths": list(record.evidence_paths),
        "remaining_blockers": blockers,
    }


def validate_provenance_acceptance(
    record: ProvenanceAcceptance,
    *,
    table_name: str = "provenance acceptance",
) -> None:
    """Validate field-level provenance acceptance semantics."""

    if not record.region_id:
        raise ValueError(f"{table_name} region_id must be non-empty")
    if not record.accepted_by:
        raise ValueError(f"{table_name} accepted_by must be non-empty")
    if not record.accepted_date:
        raise ValueError(f"{table_name} accepted_date must be non-empty")
    if not record.claim_boundary:
        raise ValueError(f"{table_name} claim_boundary must be non-empty")
    if not record.source_urls_or_citations:
        raise ValueError(f"{table_name} source_urls_or_citations must be non-empty")
    if not record.data_snapshot_paths:
        raise ValueError(f"{table_name} data_snapshot_paths must be non-empty")
    if not record.evidence_paths:
        raise ValueError(f"{table_name} evidence_paths must be non-empty")


def _acceptance_from_mapping(
    row: Mapping[str, Any],
    path: Path,
) -> ProvenanceAcceptance:
    missing = [
        field for field in REQUIRED_PROVENANCE_ACCEPTANCE_FIELDS if field not in row
    ]
    if missing:
        raise ValueError(f"{path} missing required fields: {', '.join(missing)}")
    return ProvenanceAcceptance(
        region_id=_clean(row["region_id"]),
        accepted=_bool_field(row, "accepted", path),
        accepted_by=_clean(row["accepted_by"]),
        accepted_date=_clean(row["accepted_date"]),
        source_snapshot_reviewed=_bool_field(row, "source_snapshot_reviewed", path),
        license_attribution_reviewed=_bool_field(
            row, "license_attribution_reviewed", path
        ),
        privacy_abstraction_reviewed=_bool_field(
            row, "privacy_abstraction_reviewed", path
        ),
        cache_manifest_reviewed=_bool_field(row, "cache_manifest_reviewed", path),
        reproducibility_manifest_reviewed=_bool_field(
            row, "reproducibility_manifest_reviewed", path
        ),
        source_urls_or_citations=_clean_sequence(
            row["source_urls_or_citations"],
            "source_urls_or_citations",
            path,
        ),
        data_snapshot_paths=_clean_sequence(
            row["data_snapshot_paths"],
            "data_snapshot_paths",
            path,
        ),
        evidence_paths=_clean_sequence(row["evidence_paths"], "evidence_paths", path),
        claim_boundary=_clean(row["claim_boundary"]),
    )


def _clean_sequence(value: object, field: str, path: Path) -> tuple[str, ...]:
    if not isinstance(value, Sequence) or isinstance(value, str):
        raise ValueError(f"{path} {field} must be a list of strings")
    return tuple(_clean(item) for item in value if _clean(item))


def _bool_field(row: Mapping[str, Any], field: str, path: Path) -> bool:
    value = row[field]
    if not isinstance(value, bool):
        raise ValueError(f"{path} field {field!r} must be boolean")
    return value


def _clean(value: object) -> str:
    return "" if value is None else str(value).strip()


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


__all__ = [
    "DEFAULT_PROVENANCE_ACCEPTANCE_PATH",
    "ProvenanceAcceptance",
    "REQUIRED_PROVENANCE_ACCEPTANCE_FIELDS",
    "load_provenance_acceptance",
    "summarize_provenance_acceptance",
    "validate_provenance_acceptance",
]
