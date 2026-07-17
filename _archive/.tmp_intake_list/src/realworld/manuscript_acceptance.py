"""Manuscript and report alignment acceptance record validation."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANUSCRIPT_ACCEPTANCE_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "manuscript_acceptance.json"
)

REQUIRED_MANUSCRIPT_ACCEPTANCE_FIELDS: tuple[str, ...] = (
    "region_id",
    "accepted",
    "accepted_by",
    "accepted_date",
    "paper_reviewed",
    "korean_report_reviewed",
    "docx_regenerated",
    "figure_table_manifest_reviewed",
    "evidence_gates_reviewed",
    "result_claims_aligned",
    "claim_boundary",
    "evidence_paths",
)


@dataclass(frozen=True)
class ManuscriptAcceptance:
    """One explicit manuscript/report alignment acceptance record."""

    region_id: str
    accepted: bool
    accepted_by: str
    accepted_date: str
    paper_reviewed: bool
    korean_report_reviewed: bool
    docx_regenerated: bool
    figure_table_manifest_reviewed: bool
    evidence_gates_reviewed: bool
    result_claims_aligned: bool
    claim_boundary: str
    evidence_paths: tuple[str, ...]

    @property
    def ready(self) -> bool:
        """Return whether this record can satisfy manuscript acceptance."""

        return (
            self.accepted
            and bool(self.region_id)
            and bool(self.accepted_by)
            and bool(self.accepted_date)
            and self.paper_reviewed
            and self.korean_report_reviewed
            and self.docx_regenerated
            and self.figure_table_manifest_reviewed
            and self.evidence_gates_reviewed
            and self.result_claims_aligned
            and "not operational" in self.claim_boundary.lower()
            and bool(self.evidence_paths)
        )


def load_manuscript_acceptance(
    path: str | Path = DEFAULT_MANUSCRIPT_ACCEPTANCE_PATH,
) -> ManuscriptAcceptance:
    """Load and validate a manuscript/report acceptance JSON record."""

    acceptance_path = Path(path)
    with acceptance_path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{acceptance_path} must contain a JSON object")
    record = _acceptance_from_mapping(value, acceptance_path)
    validate_manuscript_acceptance(record, table_name=str(acceptance_path))
    return record


def summarize_manuscript_acceptance(
    path: str | Path = DEFAULT_MANUSCRIPT_ACCEPTANCE_PATH,
) -> dict[str, Any]:
    """Return conservative manuscript/report acceptance readiness."""

    acceptance_path = Path(path)
    if not acceptance_path.exists():
        return {
            "acceptance_ready": False,
            "path": _display_path(acceptance_path),
            "record_present": False,
            "remaining_blockers": [
                "create an explicit manuscript/report acceptance record after evidence gates, figures, paper, report, and claim boundaries are reviewed"
            ],
        }

    record = load_manuscript_acceptance(acceptance_path)
    blockers: list[str] = []
    if not record.accepted:
        blockers.append("manuscript acceptance record does not set accepted: true")
    if not record.paper_reviewed:
        blockers.append("manuscript acceptance requires paper_reviewed: true")
    if not record.korean_report_reviewed:
        blockers.append("manuscript acceptance requires korean_report_reviewed: true")
    if not record.docx_regenerated:
        blockers.append("manuscript acceptance requires docx_regenerated: true")
    if not record.figure_table_manifest_reviewed:
        blockers.append(
            "manuscript acceptance requires figure_table_manifest_reviewed: true"
        )
    if not record.evidence_gates_reviewed:
        blockers.append("manuscript acceptance requires evidence_gates_reviewed: true")
    if not record.result_claims_aligned:
        blockers.append("manuscript acceptance requires result_claims_aligned: true")
    if "not operational" not in record.claim_boundary.lower():
        blockers.append("manuscript acceptance claim_boundary must include 'not operational'")
    if not record.evidence_paths:
        blockers.append("manuscript acceptance record must list evidence_paths")

    return {
        "acceptance_ready": not blockers,
        "path": _display_path(acceptance_path),
        "record_present": True,
        "region_id": record.region_id,
        "paper_reviewed": record.paper_reviewed,
        "korean_report_reviewed": record.korean_report_reviewed,
        "docx_regenerated": record.docx_regenerated,
        "figure_table_manifest_reviewed": record.figure_table_manifest_reviewed,
        "evidence_gates_reviewed": record.evidence_gates_reviewed,
        "result_claims_aligned": record.result_claims_aligned,
        "evidence_paths": list(record.evidence_paths),
        "remaining_blockers": blockers,
    }


def validate_manuscript_acceptance(
    record: ManuscriptAcceptance,
    *,
    table_name: str = "manuscript acceptance",
) -> None:
    """Validate field-level manuscript/report acceptance semantics."""

    if not record.region_id:
        raise ValueError(f"{table_name} region_id must be non-empty")
    if not record.accepted_by:
        raise ValueError(f"{table_name} accepted_by must be non-empty")
    if not record.accepted_date:
        raise ValueError(f"{table_name} accepted_date must be non-empty")
    if not record.claim_boundary:
        raise ValueError(f"{table_name} claim_boundary must be non-empty")
    if not record.evidence_paths:
        raise ValueError(f"{table_name} evidence_paths must be non-empty")


def _acceptance_from_mapping(
    row: Mapping[str, Any],
    path: Path,
) -> ManuscriptAcceptance:
    missing = [
        field for field in REQUIRED_MANUSCRIPT_ACCEPTANCE_FIELDS if field not in row
    ]
    if missing:
        raise ValueError(f"{path} missing required fields: {', '.join(missing)}")
    return ManuscriptAcceptance(
        region_id=_clean(row["region_id"]),
        accepted=_bool_field(row, "accepted", path),
        accepted_by=_clean(row["accepted_by"]),
        accepted_date=_clean(row["accepted_date"]),
        paper_reviewed=_bool_field(row, "paper_reviewed", path),
        korean_report_reviewed=_bool_field(row, "korean_report_reviewed", path),
        docx_regenerated=_bool_field(row, "docx_regenerated", path),
        figure_table_manifest_reviewed=_bool_field(
            row, "figure_table_manifest_reviewed", path
        ),
        evidence_gates_reviewed=_bool_field(row, "evidence_gates_reviewed", path),
        result_claims_aligned=_bool_field(row, "result_claims_aligned", path),
        claim_boundary=_clean(row["claim_boundary"]),
        evidence_paths=_clean_sequence(row["evidence_paths"], "evidence_paths", path),
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
    "DEFAULT_MANUSCRIPT_ACCEPTANCE_PATH",
    "ManuscriptAcceptance",
    "REQUIRED_MANUSCRIPT_ACCEPTANCE_FIELDS",
    "load_manuscript_acceptance",
    "summarize_manuscript_acceptance",
    "validate_manuscript_acceptance",
]
