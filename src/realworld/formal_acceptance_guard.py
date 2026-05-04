"""Guard against placeholder or template-only formal acceptance artifacts.

This audit does not approve any gate. It checks the opposite boundary: if a
formal acceptance path exists, it must not be a copied template or contain
review placeholders that could be mistaken for real acceptance evidence.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FINAL_ACCEPTANCE_ARTIFACTS: tuple[str, ...] = (
    "data/manifests/pilot_acceptance.json",
    "data/manifests/graph_scale_acceptance.json",
    "data/manifests/provenance_acceptance.json",
    "data/parameters/parameter_acceptance.csv",
    "data/parameters/road_class_overrides.csv",
    "data/manifests/validation_acceptance.json",
    "data/manifests/sensitivity_acceptance.json",
    "data/manifests/experiment_acceptance.json",
    "data/manifests/manuscript_acceptance.json",
    "data/manifests/reproducibility_acceptance.json",
    "docs/final_study_audit.md",
    "data/manifests/final_audit_acceptance.json",
)
GUARD_CLAIM_BOUNDARY = (
    "This guard detects placeholder/template misuse in formal acceptance "
    "paths. It does not create approvals, validate source claims, or mark the "
    "final study complete."
)
PLACEHOLDER_TOKENS = ("REVIEW_REQUIRED", "TEMPLATE ONLY")


@dataclass(frozen=True)
class FormalAcceptanceArtifactCheck:
    """One formal acceptance-path guard result."""

    artifact: str
    exists: bool
    status: str
    template_or_placeholder_detected: bool
    accepted_flag: str
    issue: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "artifact": self.artifact,
            "exists": self.exists,
            "status": self.status,
            "template_or_placeholder_detected": self.template_or_placeholder_detected,
            "accepted_flag": self.accepted_flag,
            "issue": self.issue,
        }


def audit_formal_acceptance_artifacts(
    *,
    project_root: str | Path = PROJECT_ROOT,
    artifacts: Sequence[str] = FINAL_ACCEPTANCE_ARTIFACTS,
) -> dict[str, Any]:
    """Return a conservative audit of formal acceptance artifact paths."""

    root = Path(project_root)
    checks = [
        _check_formal_artifact(root=root, relative_path=relative_path)
        for relative_path in artifacts
    ]
    present = [check for check in checks if check.exists]
    template_hits = [
        check for check in checks if check.template_or_placeholder_detected
    ]
    ready_candidates = [
        check for check in checks if check.status == "present_non_template"
    ]
    return {
        "claim_boundary": GUARD_CLAIM_BOUNDARY,
        "artifact_count": len(checks),
        "present_count": len(present),
        "missing_count": len(checks) - len(present),
        "template_or_placeholder_count": len(template_hits),
        "ready_candidate_count": len(ready_candidates),
        "formal_acceptance_ready": False,
        "can_mark_complete": False,
        "checks": [check.to_dict() for check in checks],
        "remaining_blockers": _remaining_blockers(checks),
    }


def _check_formal_artifact(
    *,
    root: Path,
    relative_path: str,
) -> FormalAcceptanceArtifactCheck:
    path = root / relative_path
    if not path.exists():
        return FormalAcceptanceArtifactCheck(
            artifact=relative_path,
            exists=False,
            status="missing",
            template_or_placeholder_detected=False,
            accepted_flag="absent",
            issue="formal acceptance artifact is missing",
        )
    if path.suffix.lower() == ".json":
        return _check_json_artifact(relative_path, path)
    if path.suffix.lower() == ".csv":
        return _check_csv_artifact(relative_path, path)
    if path.suffix.lower() == ".md":
        return _check_text_artifact(relative_path, path)
    return FormalAcceptanceArtifactCheck(
        artifact=relative_path,
        exists=True,
        status="present_unclassified",
        template_or_placeholder_detected=_text_contains_placeholder(
            path.read_text(encoding="utf-8", errors="replace")
        ),
        accepted_flag="unknown",
        issue="artifact exists but has no specialized guard parser",
    )


def _check_json_artifact(
    relative_path: str,
    path: Path,
) -> FormalAcceptanceArtifactCheck:
    try:
        with path.open("r", encoding="utf-8") as handle:
            value = json.load(handle)
    except json.JSONDecodeError as exc:
        return FormalAcceptanceArtifactCheck(
            artifact=relative_path,
            exists=True,
            status="invalid_json",
            template_or_placeholder_detected=False,
            accepted_flag="unknown",
            issue=f"invalid JSON: {exc}",
        )
    text = json.dumps(value, sort_keys=True)
    placeholder = _contains_placeholder(value) or _text_contains_placeholder(text)
    accepted = value.get("accepted") if isinstance(value, Mapping) else None
    template_only = bool(value.get("template_only")) if isinstance(value, Mapping) else False
    record_type = str(value.get("record_type", "")) if isinstance(value, Mapping) else ""
    if placeholder or template_only or "template" in record_type.lower():
        return FormalAcceptanceArtifactCheck(
            artifact=relative_path,
            exists=True,
            status="blocked_template_or_placeholder",
            template_or_placeholder_detected=True,
            accepted_flag=_accepted_flag(accepted),
            issue="formal JSON path contains template markers or review placeholders",
        )
    if accepted is not True:
        return FormalAcceptanceArtifactCheck(
            artifact=relative_path,
            exists=True,
            status="blocked_not_accepted",
            template_or_placeholder_detected=False,
            accepted_flag=_accepted_flag(accepted),
            issue="formal JSON path exists but accepted is not true",
        )
    return FormalAcceptanceArtifactCheck(
        artifact=relative_path,
        exists=True,
        status="present_non_template",
        template_or_placeholder_detected=False,
        accepted_flag="true",
        issue=(
            "formal JSON path is not a template by guard rules; gate-specific "
            "validators must still review it"
        ),
    )


def _check_csv_artifact(
    relative_path: str,
    path: Path,
) -> FormalAcceptanceArtifactCheck:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
    except csv.Error as exc:
        return FormalAcceptanceArtifactCheck(
            artifact=relative_path,
            exists=True,
            status="invalid_csv",
            template_or_placeholder_detected=False,
            accepted_flag="unknown",
            issue=f"invalid CSV: {exc}",
        )
    placeholder = _contains_placeholder(rows)
    accepted_values = [
        str(row.get("accepted", "")).strip().lower()
        for row in rows
        if "accepted" in row
    ]
    all_accepted = bool(accepted_values) and all(
        value == "true" for value in accepted_values
    )
    road_override_draft_values = [
        str(row.get("source_class", "")).strip().lower() for row in rows
    ]
    weak_road_override = (
        relative_path.endswith("road_class_overrides.csv")
        and any(value == "expert assumption" for value in road_override_draft_values)
    )
    if placeholder or weak_road_override:
        return FormalAcceptanceArtifactCheck(
            artifact=relative_path,
            exists=True,
            status="blocked_template_or_placeholder",
            template_or_placeholder_detected=True,
            accepted_flag=_csv_accepted_flag(accepted_values),
            issue="formal CSV path contains template markers, placeholders, or draft-only weak rows",
        )
    if accepted_values and not all_accepted:
        return FormalAcceptanceArtifactCheck(
            artifact=relative_path,
            exists=True,
            status="blocked_not_accepted",
            template_or_placeholder_detected=False,
            accepted_flag=_csv_accepted_flag(accepted_values),
            issue="formal CSV path has one or more accepted values that are not true",
        )
    return FormalAcceptanceArtifactCheck(
        artifact=relative_path,
        exists=True,
        status="present_non_template",
        template_or_placeholder_detected=False,
        accepted_flag=_csv_accepted_flag(accepted_values),
        issue=(
            "formal CSV path is not a template by guard rules; gate-specific "
            "validators must still review it"
        ),
    )


def _check_text_artifact(
    relative_path: str,
    path: Path,
) -> FormalAcceptanceArtifactCheck:
    text = path.read_text(encoding="utf-8", errors="replace")
    placeholder = _text_contains_placeholder(text)
    if placeholder or "current-state completion gap audit" in text.lower():
        return FormalAcceptanceArtifactCheck(
            artifact=relative_path,
            exists=True,
            status="blocked_template_or_placeholder",
            template_or_placeholder_detected=True,
            accepted_flag="unknown",
            issue="formal markdown path still looks like a template or gap audit",
        )
    return FormalAcceptanceArtifactCheck(
        artifact=relative_path,
        exists=True,
        status="present_non_template",
        template_or_placeholder_detected=False,
        accepted_flag="unknown",
        issue=(
            "formal markdown path is not a template by guard rules; final-audit "
            "validator must still review it"
        ),
    )


def _contains_placeholder(value: object) -> bool:
    if isinstance(value, str):
        return _text_contains_placeholder(value)
    if isinstance(value, Mapping):
        return any(_contains_placeholder(item) for item in value.values())
    if isinstance(value, Iterable):
        return any(_contains_placeholder(item) for item in value)
    return False


def _text_contains_placeholder(value: str) -> bool:
    normalized = value.upper()
    return any(token in normalized for token in PLACEHOLDER_TOKENS)


def _accepted_flag(value: object) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    if value is None:
        return "missing"
    return str(value)


def _csv_accepted_flag(values: Sequence[str]) -> str:
    if not values:
        return "not_applicable"
    unique = sorted(set(values))
    return ",".join(unique)


def _remaining_blockers(
    checks: Sequence[FormalAcceptanceArtifactCheck],
) -> list[str]:
    blockers: list[str] = []
    for check in checks:
        if check.status == "missing":
            blockers.append(f"{check.artifact}: create formal acceptance artifact")
        elif check.status != "present_non_template":
            blockers.append(f"{check.artifact}: {check.issue}")
    if not blockers:
        blockers.append(
            "gate-specific validators and final-study readiness audit must still approve all formal artifacts"
        )
    return blockers


__all__ = [
    "GUARD_CLAIM_BOUNDARY",
    "PLACEHOLDER_TOKENS",
    "FormalAcceptanceArtifactCheck",
    "FINAL_ACCEPTANCE_ARTIFACTS",
    "audit_formal_acceptance_artifacts",
]
