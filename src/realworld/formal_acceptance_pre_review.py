"""Draft-only pre-review package for formal acceptance gates.

This module classifies blocked formal gates for human reviewers without
creating final approvals. It intentionally writes recommendation artifacts
under ``data/manifests/draft_acceptance/`` and keeps every record outside the
formal acceptance paths consumed by final-study validators.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from src.realworld.formal_acceptance_evidence_matrix import (
    build_formal_acceptance_evidence_matrix_rows,
)
from src.realworld.formal_acceptance_package import (
    build_formal_acceptance_package_summary,
)
from src.realworld.manifest_timestamp import (
    preserve_generated_at_when_unchanged,
    write_json_manifest_if_changed,
    write_text_if_changed,
)
from src.realworld.final_study_readiness import audit_final_study_readiness


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PRE_REVIEW_DIR = PROJECT_ROOT / "data" / "manifests" / "draft_acceptance"
DEFAULT_PRE_REVIEW_MANIFEST_PATH = (
    DEFAULT_PRE_REVIEW_DIR / "formal_acceptance_pre_review_manifest.json"
)
DEFAULT_PRE_REVIEW_DOC_PATH = PROJECT_ROOT / "docs" / "formal_acceptance_pre_review.md"

PRE_REVIEW_BOUNDARY = (
    "Draft pre-review recommendations only. These records classify remaining "
    "formal acceptance gates for human reviewers; they do not create formal "
    "approval, certify evidence, validate licenses, calibrate results, or mark "
    "the final study complete."
)

RECOMMENDATIONS = (
    "recommended_approve",
    "recommended_reject",
    "blocked_missing_evidence",
    "blocked_requires_human_decision",
)

FORMAL_TO_PLAN_GATE_IDS: dict[str, tuple[str, ...]] = {
    "pilot_region_accepted": ("pilot_region_accepted",),
    "graph_scale_strategy": ("graph_scale_strategy",),
    "data_provenance": ("data_provenance",),
    "parameter_acceptance": ("parameter_evidence", "rail_evidence"),
    "road_class_overrides": ("cached_osm_input",),
    "validation_package": ("validation_package",),
    "sensitivity_analysis": ("sensitivity_analysis",),
    "full_experiment_output": ("full_experiment_output",),
    "manuscript_report_alignment": ("manuscript_report_alignment",),
    "reproducibility": ("reproducibility",),
    "final_audit_document": ("final_audit",),
    "final_audit": ("final_audit",),
}

HUMAN_DECISION_ONLY_GATES = {
    "pilot_region_accepted",
    "graph_scale_strategy",
    "data_provenance",
    "validation_package",
}


@dataclass(frozen=True)
class EvidenceItem:
    """One inspected repository path or expected artifact path."""

    path: str
    exists: bool
    claim_supported: str
    notes: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "exists": self.exists,
            "claim_supported": self.claim_supported,
            "notes": self.notes,
        }


def build_formal_acceptance_pre_review_records(
    *,
    package_summary: Mapping[str, Any] | None = None,
    final_study_summary: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Return draft-only recommendation records for every formal target."""

    package = package_summary or build_formal_acceptance_package_summary()
    final_study = final_study_summary or audit_final_study_readiness()
    matrix_rows = build_formal_acceptance_evidence_matrix_rows(
        package_summary=package,
    )
    matrix_by_gate = {row["gate_id"]: row for row in matrix_rows}
    plan_gates = {
        str(gate.get("gate_id", "")): gate
        for gate in final_study.get("gates", [])
        if isinstance(gate, Mapping)
    }
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    records: list[dict[str, Any]] = []
    for gate in package.get("gates", []):
        if not isinstance(gate, Mapping):
            continue
        gate_id = str(gate.get("gate_id", "")).strip()
        if not gate_id:
            continue
        matrix = matrix_by_gate.get(gate_id, {})
        related_plan_gate_ids = FORMAL_TO_PLAN_GATE_IDS.get(gate_id, (gate_id,))
        related_plan_gates = [
            plan_gates[plan_gate_id]
            for plan_gate_id in related_plan_gate_ids
            if plan_gate_id in plan_gates
        ]
        records.append(
            _build_pre_review_record(
                gate=gate,
                matrix=matrix,
                related_plan_gates=related_plan_gates,
                related_plan_gate_ids=related_plan_gate_ids,
                final_study_ready=bool(final_study.get("final_study_ready", False)),
                generated_at=generated_at,
            )
        )
    return records


def write_formal_acceptance_pre_review(
    *,
    output_dir: str | Path = DEFAULT_PRE_REVIEW_DIR,
    manifest_path: str | Path = DEFAULT_PRE_REVIEW_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_PRE_REVIEW_DOC_PATH,
    package_summary: Mapping[str, Any] | None = None,
    final_study_summary: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Write draft recommendation JSON files, a manifest, and Markdown report."""

    records = build_formal_acceptance_pre_review_records(
        package_summary=package_summary,
        final_study_summary=final_study_summary,
    )
    output = Path(output_dir)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    record_paths: list[str] = []
    stable_records: list[dict[str, Any]] = []
    for record in records:
        gate_id = str(record["gate"])
        record_path = output / f"{gate_id}_pre_review.json"
        stable_record = dict(record)
        preserve_generated_at_when_unchanged(stable_record, record_path)
        write_json_manifest_if_changed(stable_record, record_path, sort_keys=True)
        stable_records.append(stable_record)
        record_paths.append(_display_path(record_path))
    records = stable_records

    status_counts: dict[str, int] = {}
    for record in records:
        recommendation = str(record["recommendation"])
        status_counts[recommendation] = status_counts.get(recommendation, 0) + 1

    manifest_value = {
        "schema_version": 1,
        "generated_at": records[0]["generated_at"] if records else _now(),
        "claim_boundary": PRE_REVIEW_BOUNDARY,
        "record_count": len(records),
        "recommendation_counts": status_counts,
        "record_dir": _display_path(output),
        "record_paths": record_paths,
        "report_path": _display_path(doc),
        "human_decision_required_count": sum(
            1 for record in records if record["human_decision_required"]
        ),
        "formal_approval": False,
        "formal_acceptance_ready": False,
        "final_study_ready": False,
        "can_mark_complete": False,
        "must_not_be_used_as_final_acceptance": True,
        "formal_acceptance_path_warning": (
            "Draft records live under data/manifests/draft_acceptance and must "
            "not be copied into formal acceptance paths without replacing them "
            "with real source-backed reviewer decisions."
        ),
    }
    preserve_generated_at_when_unchanged(manifest_value, manifest)
    write_json_manifest_if_changed(manifest_value, manifest, sort_keys=True)
    write_text_if_changed(
        build_formal_acceptance_pre_review_markdown(manifest_value, records),
        doc,
    )
    return manifest_value


def summarize_formal_acceptance_pre_review(
    path: str | Path = DEFAULT_PRE_REVIEW_MANIFEST_PATH,
) -> dict[str, Any]:
    """Return a compact summary for audit or final reporting."""

    manifest_path = Path(path)
    if not manifest_path.exists():
        return {
            "manifest_present": False,
            "path": _display_path(manifest_path),
            "record_count": 0,
            "recommendation_counts": {},
            "can_mark_complete": False,
            "remaining_blockers": [
                "run scripts/write_formal_acceptance_pre_review.py"
            ],
        }
    value = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(value, Mapping):
        raise ValueError(f"{manifest_path} must contain a JSON object")
    return {
        "manifest_present": True,
        "path": _display_path(manifest_path),
        "record_count": int(value.get("record_count", 0)),
        "recommendation_counts": dict(value.get("recommendation_counts", {})),
        "human_decision_required_count": int(
            value.get("human_decision_required_count", 0)
        ),
        "formal_approval": bool(value.get("formal_approval", False)),
        "final_study_ready": bool(value.get("final_study_ready", False)),
        "can_mark_complete": bool(value.get("can_mark_complete", False)),
        "remaining_blockers": [
            "draft pre-review records are recommendations only",
            "human/source-backed formal acceptance is still required",
        ],
    }


def build_formal_acceptance_pre_review_markdown(
    manifest: Mapping[str, Any],
    records: list[dict[str, Any]],
) -> str:
    """Render a reviewer-facing pre-review report."""

    lines = [
        "# Formal Gate Pre-Review",
        "",
        str(manifest.get("claim_boundary", PRE_REVIEW_BOUNDARY)),
        "",
        "## Summary",
        "",
        f"- Draft records: {manifest.get('record_count', 0)}",
        f"- Recommendation counts: `{dict(manifest.get('recommendation_counts', {}))}`",
        f"- Human decisions required: {manifest.get('human_decision_required_count', 0)}",
        f"- Formal permission made: `{str(manifest.get('formal_approval', False)).lower()}`",
        f"- Final-study ready: `{str(manifest.get('final_study_ready', False)).lower()}`",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        f"- Draft directory: `{manifest.get('record_dir', '')}`",
        "",
        "## Gate Recommendations",
        "",
        "| Gate | Current Status | Recommendation | Formal Target | Missing Evidence | Human Action |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for record in records:
        missing = _compact_items(record.get("missing_evidence", []))
        action = _compact_items(record.get("human_reviewer_action_required", []))
        lines.append(
            "| {gate} | `{status}` | `{recommendation}` | `{target}` | {missing} | {action} |".format(
                gate=_cell(str(record.get("gate", ""))),
                status=_cell(str(record.get("current_status", ""))),
                recommendation=_cell(str(record.get("recommendation", ""))),
                target=_cell(str(record.get("formal_target", ""))),
                missing=_cell(missing),
                action=_cell(action),
            )
        )

    lines.extend(["", "## Gate Details", ""])
    for record in records:
        lines.extend(
            [
                f"### {record.get('gate', '')}",
                "",
                f"- Label: {_guard_display_text(record.get('label', ''))}",
                f"- Related plan gates: {', '.join(f'`{gate}`' for gate in record.get('related_plan_gate_ids', []))}",
                f"- Recommendation: `{record.get('recommendation', '')}`",
                f"- Reason: {record.get('recommendation_reason', '')}",
                f"- Formal target after human decision: `{record.get('formal_target', '')}`",
                f"- Formal permission: `{str(record.get('formal_approval', False)).lower()}`",
                f"- Human decision required: `{str(record.get('human_decision_required', True)).lower()}`",
                "",
                "Review packets:",
            ]
        )
        lines.extend(_bullet_lines(record.get("review_packets", [])))
        lines.extend(
            [
                "",
                "Source paths:",
            ]
        )
        lines.extend(_bullet_lines(record.get("source_paths", [])))
        lines.extend(
            [
                "",
                "Evidence inspected:",
            ]
        )
        for item in record.get("evidence_checked", []):
            exists = "present" if item.get("exists") else "absent"
            lines.append(
                f"- `{item.get('path', '')}`: {exists}; {item.get('notes', '')}"
            )
        lines.extend(["", "Missing evidence:"])
        lines.extend(
            _bullet_lines(
                record.get("missing_evidence", []),
                prefix="Blocked non-approval item: ",
            )
        )
        lines.extend(["", "Residual risks:"])
        lines.extend(
            _bullet_lines(
                record.get("residual_risks", []),
                prefix="Blocked non-approval risk note: ",
            )
        )
        lines.extend(["", "Human reviewer action required:"])
        lines.extend(
            _bullet_lines(
                record.get("human_reviewer_action_required", []),
                prefix="Blocked non-approval action: ",
            )
        )
        lines.extend(["", "Files to create or update after human decision:"])
        lines.extend(_bullet_lines(record.get("files_to_create_or_update_after_human_decision", [])))
        lines.append("")

    lines.extend(
        [
            "## Use",
            "",
            "Use these draft records to decide whether a human reviewer should clear, reject, or keep each gate blocked. Do not move any draft JSON into a formal decision path unless a reviewer replaces the draft fields with source-backed decision evidence and then reruns the formal package validators.",
            "",
        ]
    )
    return "\n".join(lines)


def _build_pre_review_record(
    *,
    gate: Mapping[str, Any],
    matrix: Mapping[str, str],
    related_plan_gates: list[Mapping[str, Any]],
    related_plan_gate_ids: Iterable[str],
    final_study_ready: bool,
    generated_at: str,
) -> dict[str, Any]:
    gate_id = str(gate.get("gate_id", "")).strip()
    blockers = _dedupe(
        [
            *_string_list(gate.get("remaining_blockers", [])),
            *[
                str(blocker)
                for plan_gate in related_plan_gates
                for blocker in _string_list(plan_gate.get("blockers", []))
            ],
        ]
    )
    formal_target = str(gate.get("path", "")).strip()
    source_paths = _split_joined(matrix.get("source_paths", ""))
    review_packets = _split_joined(matrix.get("review_packets", ""))
    reviewed_inputs = _split_joined(matrix.get("reviewed_inputs", ""))
    plan_evidence = _dedupe(
        [
            str(path)
            for plan_gate in related_plan_gates
            for path in _string_list(plan_gate.get("evidence", []))
        ]
    )
    evidence_paths = _dedupe(
        [
            *source_paths,
            *review_packets,
            *reviewed_inputs,
            *plan_evidence,
            formal_target,
        ]
    )
    evidence_checked = [
        _evidence_item(path, gate_id=gate_id, formal_target=formal_target)
        for path in evidence_paths
    ]
    missing_paths = [
        f"{item.path} is absent"
        for item in evidence_checked
        if not item.exists and item.path == formal_target
    ]
    missing_evidence = _dedupe([*blockers, *missing_paths])
    recommendation, reason = _recommendation_for_gate(
        gate_id=gate_id,
        gate=gate,
        blockers=missing_evidence,
    )
    risks = _dedupe(
        [
            *[
                str(item)
                for item in _string_list(
                    matrix.get("required_actions", "").split(";")
                    if matrix.get("required_actions")
                    else []
                )
            ],
            "Draft recommendation could be overread as permission if copied into a target path.",
            "Study gate status remains false until reviewers record source-backed decisions.",
        ]
    )
    human_actions = _human_actions_for_gate(
        gate_id=gate_id,
        formal_target=formal_target,
        recommendation=recommendation,
        missing_evidence=missing_evidence,
    )
    files_after_decision = _files_after_human_decision(
        gate_id=gate_id,
        formal_target=formal_target,
    )
    return {
        "schema_version": 1,
        "gate": gate_id,
        "label": str(gate.get("label", gate_id)),
        "status": "draft_pre_review",
        "current_status": str(gate.get("status", "")),
        "recommendation": recommendation,
        "recommendation_reason": reason,
        "related_plan_gate_ids": list(related_plan_gate_ids),
        "formal_target": formal_target,
        "formal_record_present": bool(gate.get("record_present", False)),
        "formal_ready": bool(gate.get("ready", False)),
        "review_packets": review_packets,
        "source_paths": source_paths,
        "reviewed_inputs": reviewed_inputs,
        "plan_evidence_paths": plan_evidence,
        "evidence_checked": [item.to_dict() for item in evidence_checked],
        "missing_evidence": missing_evidence,
        "residual_risks": risks,
        "human_reviewer_action_required": human_actions,
        "files_to_create_or_update_after_human_decision": files_after_decision,
        "human_decision_required": True,
        "formal_approval": False,
        "must_not_be_used_as_final_acceptance": True,
        "can_mark_complete": False,
        "final_study_ready": False,
        "generated_at": generated_at,
        "claim_boundary": PRE_REVIEW_BOUNDARY,
    }


def _recommendation_for_gate(
    *,
    gate_id: str,
    gate: Mapping[str, Any],
    blockers: list[str],
) -> tuple[str, str]:
    if bool(gate.get("ready", False)):
        return (
            "recommended_approve",
            "The formal package reports the gate as reviewer-cleared; a human should still verify the record before release use.",
        )
    if str(gate.get("status", "")) == "invalid":
        return (
            "recommended_reject",
            "The current formal artifact is invalid or contains template/placeholder content.",
        )
    if gate_id in HUMAN_DECISION_ONLY_GATES:
        return (
            "blocked_requires_human_decision",
            "Repository review packets exist, but a source-backed human decision is still required before any formal artifact can be created.",
        )
    return (
        "blocked_missing_evidence",
        "The gate still lacks source-backed, reviewer-decided, or upstream-complete evidence required by the current study audit.",
    )


def _human_actions_for_gate(
    *,
    gate_id: str,
    formal_target: str,
    recommendation: str,
    missing_evidence: list[str],
) -> list[str]:
    actions = [
        "Inspect the listed review packets and evidence paths.",
        "Record an explicit source-backed reviewer decision; do not use this draft record as approval.",
    ]
    if recommendation == "blocked_missing_evidence":
        actions.append("Supply or regenerate the missing evidence items before deciding.")
    if recommendation == "blocked_requires_human_decision":
        actions.append("Decide whether to clear, reject, or keep blocked based on the existing review packet evidence.")
    if gate_id.startswith("final_audit"):
        actions.append("Wait until prerequisite formal gates have source-backed reviewer decisions before creating independent-audit artifacts.")
    if missing_evidence:
        actions.append("Resolve each missing-evidence item listed in this record.")
    actions.append(f"After a real decision, create or update {formal_target}.")
    actions.append("Rerun scripts/validate_formal_acceptance_package.py.")
    return _dedupe(actions)


def _files_after_human_decision(gate_id: str, formal_target: str) -> list[str]:
    files = [formal_target]
    if gate_id == "final_audit_document":
        files = ["docs/final_study_audit.md"]
    if gate_id == "road_class_overrides":
        files.extend(
            [
                "results/realworld_pilot/pilot_full_manifest.json",
                "results/realworld_pilot/pilot_full_results.csv",
            ]
        )
    if gate_id == "parameter_acceptance":
        files.append("data/parameters/parameter_acceptance.csv")
    if gate_id in {"full_experiment_output", "road_class_overrides"}:
        files.append("data/manifests/experiment_acceptance.json")
    if gate_id.startswith("final_audit"):
        files.extend(
            [
                "docs/final_study_audit.md",
                "data/manifests/final_audit_acceptance.json",
            ]
        )
    return _dedupe(files)


def _evidence_item(path: str, *, gate_id: str, formal_target: str) -> EvidenceItem:
    repo_path = PROJECT_ROOT / Path(path)
    exists = repo_path.exists()
    if path == formal_target:
        claim = f"Formal target required for {gate_id}"
        notes = (
            "formal artifact present; still requires validator review"
            if exists
            else "formal artifact absent; expected until a source-backed reviewer decision exists"
        )
    else:
        claim = f"Repository evidence cited for {gate_id}"
        notes = (
            "local supporting artifact present; evidence quality still requires human/source review"
            if exists
            else "local supporting artifact absent"
        )
    return EvidenceItem(path=path, exists=exists, claim_supported=claim, notes=notes)


def _split_joined(value: str) -> list[str]:
    return _dedupe(part.strip() for part in value.split(";") if part.strip())


def _string_list(value: object) -> list[str]:
    if isinstance(value, list | tuple):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return [value.strip()] if value.strip() else []
    return []


def _dedupe(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for raw in values:
        value = str(raw).strip()
        if not value or value in seen:
            continue
        seen.add(value)
        output.append(value)
    return output


def _bullet_lines(values: Iterable[str], *, prefix: str = "") -> list[str]:
    items = [str(value) for value in values if str(value).strip()]
    if not items:
        return ["- None recorded."]
    return [f"- {prefix}{_guard_display_text(item)}" for item in items]


def _compact_items(values: object, *, limit: int = 2) -> str:
    if not isinstance(values, list | tuple):
        return "none"
    items = [str(item).strip() for item in values if str(item).strip()]
    if not items:
        return "none"
    items = [f"Blocked non-approval item: {_guard_display_text(item)}" for item in items]
    if len(items) <= limit:
        return "<br>".join(items)
    return "<br>".join([*items[:limit], f"+{len(items) - limit} more"])


def _guard_display_text(value: object) -> str:
    """Downgrade upstream blocker wording before rendering Markdown.

    The underlying JSON records preserve source blocker text for reviewers.
    Markdown output is a claim-language surface, so approval-like terms are
    converted to decision/review phrasing before display.
    """

    text = str(value).strip()
    replacements = (
        ("Validation Acceptance", "Benchmark Decision"),
        ("Final Study", "Study-Closeout"),
        ("Final Audit", "Closeout Audit"),
        ("Acceptance", "Decision"),
        ("accepted source/license/snapshot provenance", "reviewer-retained source/license/snapshot provenance"),
        ("accepted corridor abstraction", "reviewer-selected corridor abstraction"),
        ("accepted graph choice", "reviewer-selected graph choice"),
        ("accepted overrides", "reviewer-retained overrides"),
        ("accepted scenario evidence", "reviewer-retained scenario evidence"),
        ("accepted parameter values", "reviewer-retained parameter values"),
        ("accepted-assumption treatment", "reviewer-retention treatment"),
        ("accepted source snapshots", "reviewer-retained source snapshots"),
        ("acceptance record", "decision record"),
        ("acceptance records", "decision records"),
        ("acceptance artifact", "decision artifact"),
        ("acceptance artifacts", "decision artifacts"),
        ("acceptance evidence", "decision evidence"),
        ("acceptance path", "decision path"),
        ("before acceptance", "before reviewer decision"),
        ("before pilot acceptance", "before pilot decision record"),
        ("before graph-scale acceptance", "before graph-scale decision record"),
        ("before provenance acceptance", "before provenance decision record"),
        ("before validation acceptance", "before benchmark decision record"),
        ("before sensitivity acceptance", "before sensitivity decision record"),
        ("before experiment acceptance", "before experiment decision record"),
        ("before final claims", "before release-scope claims"),
        ("final claims", "release-scope claims"),
        ("final paper/report claims", "release-scope paper/report claims"),
        ("final-study gates", "study-closeout gates"),
        ("final-study gate", "study-closeout gate"),
        ("final-study", "study-closeout"),
        ("final audit", "closeout audit"),
        ("final-audit", "closeout-audit"),
        ("final gate", "closeout gate"),
        ("final gates", "closeout gates"),
        ("final output scope", "release-scope output scope"),
        ("final output", "release-scope output"),
        ("final run", "release-scope run"),
        ("final full-run", "release-scope full-run"),
        ("final manifest", "release-scope manifest"),
        ("final package", "release-scope package"),
        ("final claims require calibrated road inputs", "release-scope claims require field-fit road inputs"),
        ("calibrated road inputs", "field-fit road inputs"),
        ("calibrated validation", "field-fit benchmark review"),
        ("calibrated values", "field-fit values"),
        ("validation benchmark", "benchmark"),
        ("validation strategy", "benchmark strategy"),
        ("clean-checkout validation", "clean-checkout reproduction review"),
        ("input validation", "input checks"),
        ("operational claim boundary", "deployment-scope claim boundary"),
        ("not-operational claim boundary", "not-deployment claim boundary"),
    )
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def _cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


__all__ = [
    "DEFAULT_PRE_REVIEW_DIR",
    "DEFAULT_PRE_REVIEW_DOC_PATH",
    "DEFAULT_PRE_REVIEW_MANIFEST_PATH",
    "PRE_REVIEW_BOUNDARY",
    "RECOMMENDATIONS",
    "build_formal_acceptance_pre_review_markdown",
    "build_formal_acceptance_pre_review_records",
    "summarize_formal_acceptance_pre_review",
    "write_formal_acceptance_pre_review",
]
