"""Focused final-audit decision worksheet.

The current-goal completion audit and formal acceptance intake artifacts expose
why the final-audit gate is still blocked. This module turns that current state
into final-audit decision rows without creating ``docs/final_study_audit.md`` or
``data/manifests/final_audit_acceptance.json``.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from src.realworld.final_audit_acceptance import (
    DEFAULT_FINAL_AUDIT_ACCEPTANCE_PATH,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CURRENT_GOAL_COMPLETION_AUDIT_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "current_goal_completion_audit.json"
)
DEFAULT_FORMAL_ACCEPTANCE_PACKAGE_AUDIT_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "formal_acceptance_package_audit.json"
)
DEFAULT_FORMAL_ACCEPTANCE_EVIDENCE_MATRIX_MANIFEST_PATH = (
    PROJECT_ROOT
    / "data"
    / "manifests"
    / "formal_acceptance_evidence_matrix_manifest.json"
)
DEFAULT_ACCEPTANCE_ORCHESTRATION_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "acceptance_orchestration_manifest.json"
)
DEFAULT_FINAL_STUDY_AUDIT_PATH = PROJECT_ROOT / "docs" / "final_study_audit.md"
DEFAULT_FINAL_AUDIT_DECISION_PACKET_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "final_audit_decision_packet.csv"
)
DEFAULT_FINAL_AUDIT_DECISION_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "final_audit_decision_manifest.json"
)
DEFAULT_FINAL_AUDIT_DECISION_DOC_PATH = (
    PROJECT_ROOT / "docs" / "final_audit_decision_packet.md"
)
FINAL_AUDIT_DECISION_SCOPE = (
    "Final-audit decision packet only; not final-audit acceptance, not "
    "docs/final_study_audit.md, not calibrated real-world validation, not "
    "final-study approval, and not operational routing evidence."
)
FINAL_AUDIT_DECISION_COLUMNS: tuple[str, ...] = (
    "decision_id",
    "decision_topic",
    "candidate_decision",
    "current_evidence",
    "decision_status",
    "blocking_reason",
    "required_reviewer_action",
    "followup_artifacts",
    "evidence_input_paths",
    "can_support_final_audit_acceptance",
    "claim_boundary",
)


def build_final_audit_decision_rows(
    *,
    goal_completion_audit_path: str
    | Path = DEFAULT_CURRENT_GOAL_COMPLETION_AUDIT_PATH,
    formal_package_audit_path: str | Path = DEFAULT_FORMAL_ACCEPTANCE_PACKAGE_AUDIT_PATH,
    evidence_matrix_manifest_path: str
    | Path = DEFAULT_FORMAL_ACCEPTANCE_EVIDENCE_MATRIX_MANIFEST_PATH,
    acceptance_orchestration_manifest_path: str
    | Path = DEFAULT_ACCEPTANCE_ORCHESTRATION_MANIFEST_PATH,
    final_study_audit_path: str | Path = DEFAULT_FINAL_STUDY_AUDIT_PATH,
    final_audit_acceptance_path: str | Path = DEFAULT_FINAL_AUDIT_ACCEPTANCE_PATH,
) -> list[dict[str, str]]:
    """Return reviewer rows for final-audit gate decisions."""

    goal_audit = _read_json_object(goal_completion_audit_path)
    formal_package = _read_json_object(formal_package_audit_path)
    evidence_matrix = _read_json_object(evidence_matrix_manifest_path)
    orchestration = _read_json_object(acceptance_orchestration_manifest_path)
    audit_doc = Path(final_study_audit_path)
    acceptance_path = Path(final_audit_acceptance_path)
    blocked_gate_ids = _string_list(goal_audit.get("blocked_gate_ids", []))
    blocked_pre_final = [gate for gate in blocked_gate_ids if gate != "final_audit"]
    missing_artifacts = _string_list(
        goal_audit.get("missing_acceptance_artifacts", [])
    )
    proxy_signals = _string_list(goal_audit.get("proxy_signals_rejected", []))
    evidence_paths = _evidence_paths(
        goal_completion_audit_path=goal_completion_audit_path,
        formal_package_audit_path=formal_package_audit_path,
        evidence_matrix_manifest_path=evidence_matrix_manifest_path,
        acceptance_orchestration_manifest_path=acceptance_orchestration_manifest_path,
        final_study_audit_path=final_study_audit_path,
        final_audit_acceptance_path=final_audit_acceptance_path,
    )

    return [
        _row(
            decision_id="pre_final_gate_closure_decision",
            decision_topic="Pre-final gate closure",
            candidate_decision=(
                "Run the final audit only after every pre-final gate is ready "
                "and the current goal-completion checklist has no blocked "
                "pre-final gate"
            ),
            current_evidence=_goal_gate_evidence(goal_audit, blocked_pre_final),
            decision_status=(
                "blocked_pre_final_gates_not_ready"
                if blocked_pre_final
                else "needs_human_review_pre_final_gate_closure"
            ),
            blocking_reason=(
                "pre-final gates remain blocked: " + ", ".join(blocked_pre_final)
                if blocked_pre_final
                else ""
            ),
            required_reviewer_action=(
                "Confirm every non-final gate has source-backed acceptance "
                "before authoring the independent final audit."
            ),
            followup_artifacts=(
                "data/manifests/current_goal_completion_audit.json; "
                "docs/final_study_audit.md"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            decision_id="formal_acceptance_artifact_decision",
            decision_topic="Formal acceptance artifacts",
            candidate_decision=(
                "Accept final-audit scope only after all named formal "
                "acceptance artifacts are present, reviewed, and non-template"
            ),
            current_evidence=_formal_artifact_evidence(goal_audit, formal_package),
            decision_status=(
                "blocked_missing_formal_acceptance_artifacts"
                if missing_artifacts
                else "needs_human_review_formal_acceptance_artifacts"
            ),
            blocking_reason=(
                "required formal acceptance artifacts are absent: "
                + ", ".join(missing_artifacts)
                if missing_artifacts
                else ""
            ),
            required_reviewer_action=(
                "Review the formal acceptance package and confirm no required "
                "artifact is missing, invalid, copied from a template, or still "
                "a placeholder."
            ),
            followup_artifacts=(
                "data/manifests/formal_acceptance_package_audit.json; "
                "data/manifests/final_audit_acceptance.json"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            decision_id="final_study_audit_document_decision",
            decision_topic="Final-study audit document",
            candidate_decision=(
                "Write docs/final_study_audit.md only after all pre-final gates "
                "close and the independent prompt-to-artifact checklist can be "
                "completed without proxy evidence"
            ),
            current_evidence=_audit_document_evidence(audit_doc),
            decision_status=(
                "needs_human_review_final_study_audit_document"
                if audit_doc.exists()
                else "blocked_missing_final_study_audit_document"
            ),
            blocking_reason=(
                "" if audit_doc.exists() else "docs/final_study_audit.md is absent"
            ),
            required_reviewer_action=(
                "Author and review the final-study audit document only after "
                "upstream acceptance records close."
            ),
            followup_artifacts="docs/final_study_audit.md",
            evidence_input_paths=evidence_paths,
        ),
        _row(
            decision_id="final_audit_acceptance_boundary",
            decision_topic="Formal final-audit acceptance boundary",
            candidate_decision=(
                "Create final_audit_acceptance.json only after prompt-to-artifact "
                "review confirms the current gate list, all gate evidence, no "
                "proxy completion, and the not-operational claim boundary"
            ),
            current_evidence=(
                f"final_audit_acceptance_present={str(acceptance_path.exists()).lower()}"
            ),
            decision_status=(
                "needs_human_review_formal_final_audit_acceptance"
                if acceptance_path.exists()
                else "blocked_missing_final_audit_acceptance_record"
            ),
            blocking_reason=(
                ""
                if acceptance_path.exists()
                else "data/manifests/final_audit_acceptance.json is absent"
            ),
            required_reviewer_action=(
                "Record formal final-audit acceptance only after the final audit "
                "document and all pre-final acceptance artifacts are reviewed."
            ),
            followup_artifacts="data/manifests/final_audit_acceptance.json",
            evidence_input_paths=evidence_paths,
        ),
        _row(
            decision_id="proxy_signal_rejection_decision",
            decision_topic="Proxy completion signal rejection",
            candidate_decision=(
                "Confirm tests, generated artifacts, review packets, smoke "
                "manifests, and green audits are supporting evidence only, not "
                "final-study completion"
            ),
            current_evidence=_proxy_signal_evidence(proxy_signals),
            decision_status="needs_human_review_proxy_signal_boundary",
            blocking_reason="",
            required_reviewer_action=(
                "Review the proxy-signal list and keep final completion blocked "
                "until formal acceptance artifacts close every gate."
            ),
            followup_artifacts=(
                "data/manifests/current_goal_completion_audit.json; "
                "data/manifests/final_audit_acceptance.json"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            decision_id="review_packet_handoff_decision",
            decision_topic="Review-packet handoff completeness",
            candidate_decision=(
                "Use the existing orchestration, evidence matrix, and formal "
                "package audits as reviewer intake only until final acceptance "
                "records are supplied"
            ),
            current_evidence=_review_handoff_evidence(
                formal_package,
                evidence_matrix,
                orchestration,
            ),
            decision_status="needs_human_review_final_packet_handoff",
            blocking_reason="",
            required_reviewer_action=(
                "Confirm each review packet has an assigned reviewer path and "
                "that handoff artifacts do not approve evidence by themselves."
            ),
            followup_artifacts=(
                "data/manifests/acceptance_orchestration_manifest.json; "
                "data/manifests/formal_acceptance_evidence_matrix_manifest.json"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            decision_id="not_operational_claim_boundary_decision",
            decision_topic="Not-operational claim boundary",
            candidate_decision=(
                "Accept final-audit language only if it preserves the "
                "decision-support, non-operational, non-calibrated boundary "
                "until all source-backed gates close"
            ),
            current_evidence=_claim_boundary_evidence(goal_audit),
            decision_status="needs_human_review_not_operational_boundary",
            blocking_reason="",
            required_reviewer_action=(
                "Review final-audit wording so the study is not presented as "
                "an operational route plan, calibrated forecast, or emergency "
                "deployment instruction."
            ),
            followup_artifacts=(
                "docs/final_study_audit.md; "
                "data/manifests/final_audit_acceptance.json"
            ),
            evidence_input_paths=evidence_paths,
        ),
    ]


def write_final_audit_decision_packet(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_FINAL_AUDIT_DECISION_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_FINAL_AUDIT_DECISION_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_FINAL_AUDIT_DECISION_DOC_PATH,
    goal_completion_audit_path: str
    | Path = DEFAULT_CURRENT_GOAL_COMPLETION_AUDIT_PATH,
    formal_package_audit_path: str | Path = DEFAULT_FORMAL_ACCEPTANCE_PACKAGE_AUDIT_PATH,
    evidence_matrix_manifest_path: str
    | Path = DEFAULT_FORMAL_ACCEPTANCE_EVIDENCE_MATRIX_MANIFEST_PATH,
    acceptance_orchestration_manifest_path: str
    | Path = DEFAULT_ACCEPTANCE_ORCHESTRATION_MANIFEST_PATH,
    final_study_audit_path: str | Path = DEFAULT_FINAL_STUDY_AUDIT_PATH,
    final_audit_acceptance_path: str | Path = DEFAULT_FINAL_AUDIT_ACCEPTANCE_PATH,
) -> dict[str, Any]:
    """Write CSV, JSON, and Markdown final-audit decision artifacts."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FINAL_AUDIT_DECISION_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    column: str(row.get(column, ""))
                    for column in FINAL_AUDIT_DECISION_COLUMNS
                }
            )

    summary = build_final_audit_decision_manifest(
        rows=rows,
        output_path=output,
        manifest_path=manifest,
        doc_path=doc,
        goal_completion_audit_path=goal_completion_audit_path,
        formal_package_audit_path=formal_package_audit_path,
        evidence_matrix_manifest_path=evidence_matrix_manifest_path,
        acceptance_orchestration_manifest_path=acceptance_orchestration_manifest_path,
        final_study_audit_path=final_study_audit_path,
        final_audit_acceptance_path=final_audit_acceptance_path,
    )
    manifest.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    doc.write_text(build_final_audit_decision_markdown(summary, rows=rows), encoding="utf-8")
    return summary


def build_final_audit_decision_manifest(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_FINAL_AUDIT_DECISION_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_FINAL_AUDIT_DECISION_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_FINAL_AUDIT_DECISION_DOC_PATH,
    goal_completion_audit_path: str
    | Path = DEFAULT_CURRENT_GOAL_COMPLETION_AUDIT_PATH,
    formal_package_audit_path: str | Path = DEFAULT_FORMAL_ACCEPTANCE_PACKAGE_AUDIT_PATH,
    evidence_matrix_manifest_path: str
    | Path = DEFAULT_FORMAL_ACCEPTANCE_EVIDENCE_MATRIX_MANIFEST_PATH,
    acceptance_orchestration_manifest_path: str
    | Path = DEFAULT_ACCEPTANCE_ORCHESTRATION_MANIFEST_PATH,
    final_study_audit_path: str | Path = DEFAULT_FINAL_STUDY_AUDIT_PATH,
    final_audit_acceptance_path: str | Path = DEFAULT_FINAL_AUDIT_ACCEPTANCE_PATH,
) -> dict[str, Any]:
    """Return a conservative final-audit decision manifest."""

    statuses = _counts(row.get("decision_status", "") for row in rows)
    blocking_count = sum(
        1 for row in rows if str(row.get("decision_status", "")).startswith("blocked")
    )
    human_count = sum(
        1
        for row in rows
        if str(row.get("decision_status", "")).startswith("needs_human_review")
    )
    return {
        "schema_version": 1,
        "claim_boundary": (
            FINAL_AUDIT_DECISION_SCOPE
            + " It cannot create or replace docs/final_study_audit.md or "
            "data/manifests/final_audit_acceptance.json."
        ),
        "result_scope": FINAL_AUDIT_DECISION_SCOPE,
        "row_count": len(rows),
        "decision_status_counts": statuses,
        "blocking_decision_count": blocking_count,
        "human_review_decision_count": human_count,
        "pre_final_gate_closure_decision_recorded": False,
        "formal_acceptance_artifact_decision_recorded": False,
        "final_study_audit_document_decision_recorded": False,
        "final_audit_decision_recorded": False,
        "final_study_audit_document_present": Path(final_study_audit_path).exists(),
        "final_audit_acceptance_record_present": Path(
            final_audit_acceptance_path
        ).exists(),
        "final_audit_gate_closure_candidate_count": 0,
        "publication_ready": False,
        "can_mark_complete": False,
        "inputs": {
            "goal_completion_audit": _display_path(Path(goal_completion_audit_path)),
            "formal_acceptance_package_audit": _display_path(
                Path(formal_package_audit_path)
            ),
            "formal_acceptance_evidence_matrix_manifest": _display_path(
                Path(evidence_matrix_manifest_path)
            ),
            "acceptance_orchestration_manifest": _display_path(
                Path(acceptance_orchestration_manifest_path)
            ),
            "final_study_audit": _display_path(Path(final_study_audit_path)),
            "final_audit_acceptance": _display_path(Path(final_audit_acceptance_path)),
        },
        "outputs": {
            "csv": _display_path(Path(output_path)),
            "manifest": _display_path(Path(manifest_path)),
            "doc": _display_path(Path(doc_path)),
        },
        "review_items": [
            "confirm all pre-final gates are ready before final audit",
            "confirm every required formal acceptance artifact is reviewed and non-template",
            "author docs/final_study_audit.md only after upstream acceptance closes",
            "record final_audit_acceptance.json only after prompt-to-artifact review",
            "preserve the not-operational claim boundary in final-audit wording",
        ],
        "remaining_blockers": _remaining_blockers(rows),
    }


def build_final_audit_decision_markdown(
    manifest: Mapping[str, Any],
    *,
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Return a human-readable final-audit decision packet."""

    lines = [
        "# Study Closeout Review Packet",
        "",
        str(manifest.get("claim_boundary", FINAL_AUDIT_DECISION_SCOPE)),
        "",
        "## Verdict",
        "",
        f"- Publication ready: `{str(manifest.get('publication_ready', False)).lower()}`",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        f"- Decision rows: {manifest.get('row_count', 0)}",
        f"- Blocking decisions: {manifest.get('blocking_decision_count', 0)}",
        f"- Human-review decisions: {manifest.get('human_review_decision_count', 0)}",
        f"- Status counts: `{manifest.get('decision_status_counts', {})}`",
        "",
        "## Decision Rows",
        "",
        "| Decision | Status | Evidence | Required Action |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {decision} | {status} | {evidence} | {action} |".format(
                decision=_cell(row.get("decision_id", "")),
                status=_cell(row.get("decision_status", "")),
                evidence=_cell(row.get("current_evidence", "")),
                action=_cell(row.get("required_reviewer_action", "")),
            )
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This packet does not approve the final audit or final-study completion.",
            "- It does not replace pre-final gate acceptance, prompt-to-artifact review, or formal final-audit acceptance.",
            "- Keep `docs/final_study_audit.md` and `data/manifests/final_audit_acceptance.json` absent until every pre-final gate is accepted.",
            "",
        ]
    )
    return "\n".join(lines)


def _row(
    *,
    decision_id: str,
    decision_topic: str,
    candidate_decision: str,
    current_evidence: str,
    decision_status: str,
    blocking_reason: str,
    required_reviewer_action: str,
    followup_artifacts: str,
    evidence_input_paths: str,
) -> dict[str, str]:
    return {
        "decision_id": decision_id,
        "decision_topic": decision_topic,
        "candidate_decision": candidate_decision,
        "current_evidence": current_evidence,
        "decision_status": decision_status,
        "blocking_reason": blocking_reason,
        "required_reviewer_action": required_reviewer_action,
        "followup_artifacts": followup_artifacts,
        "evidence_input_paths": evidence_input_paths,
        "can_support_final_audit_acceptance": "false",
        "claim_boundary": FINAL_AUDIT_DECISION_SCOPE,
    }


def _read_json_object(path: str | Path) -> dict[str, Any]:
    json_path = Path(path)
    if not json_path.exists():
        return {}
    with json_path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{json_path} must contain a JSON object")
    return value


def _goal_gate_evidence(
    goal_audit: Mapping[str, Any],
    blocked_pre_final: Sequence[str],
) -> str:
    return (
        f"final_study_ready={str(goal_audit.get('final_study_ready', False)).lower()}; "
        f"ready_gate_count={goal_audit.get('ready_gate_count', 0)}; "
        f"blocked_gate_count={goal_audit.get('blocked_gate_count', 0)}; "
        f"blocked_pre_final_gate_count={len(blocked_pre_final)}; "
        f"blocked_pre_final_gates={','.join(blocked_pre_final)}"
    )


def _formal_artifact_evidence(
    goal_audit: Mapping[str, Any],
    formal_package: Mapping[str, Any],
) -> str:
    return (
        f"missing_acceptance_artifact_count={goal_audit.get('missing_acceptance_artifact_count', 0)}; "
        f"formal_package_ready={str(formal_package.get('formal_acceptance_ready', False)).lower()}; "
        f"formal_package_ready_gate_count={formal_package.get('ready_gate_count', 0)}; "
        f"formal_package_blocked_gate_count={formal_package.get('blocked_gate_count', 0)}; "
        f"formal_package_invalid_gate_count={formal_package.get('invalid_gate_count', 0)}"
    )


def _audit_document_evidence(path: Path) -> str:
    size = path.stat().st_size if path.exists() else 0
    return (
        f"final_study_audit_present={str(path.exists()).lower()}; "
        f"final_study_audit_size_bytes={size}"
    )


def _proxy_signal_evidence(proxy_signals: Sequence[str]) -> str:
    if not proxy_signals:
        return "proxy_signal_count=0"
    return (
        f"proxy_signal_count={len(proxy_signals)}; "
        f"proxy_signals={'; '.join(proxy_signals)}"
    )


def _review_handoff_evidence(
    formal_package: Mapping[str, Any],
    evidence_matrix: Mapping[str, Any],
    orchestration: Mapping[str, Any],
) -> str:
    return (
        f"formal_package_gate_count={formal_package.get('gate_count', 0)}; "
        f"evidence_matrix_row_count={evidence_matrix.get('row_count', 0)}; "
        f"evidence_matrix_human_decision_required_count={evidence_matrix.get('human_decision_required_count', 0)}; "
        f"orchestration_record_count={orchestration.get('record_count', 0)}; "
        f"orchestration_blocked_or_review_record_count={orchestration.get('blocked_or_review_record_count', 0)}"
    )


def _claim_boundary_evidence(goal_audit: Mapping[str, Any]) -> str:
    return (
        f"claim_boundary={goal_audit.get('claim_boundary', '')}; "
        f"result_scope={goal_audit.get('result_scope', '')}; "
        f"next_required_input={goal_audit.get('next_required_input', '')}"
    )


def _evidence_paths(
    *,
    goal_completion_audit_path: str | Path,
    formal_package_audit_path: str | Path,
    evidence_matrix_manifest_path: str | Path,
    acceptance_orchestration_manifest_path: str | Path,
    final_study_audit_path: str | Path,
    final_audit_acceptance_path: str | Path,
) -> str:
    paths = [
        Path(goal_completion_audit_path),
        PROJECT_ROOT / "docs" / "current_goal_completion_audit.md",
        Path(formal_package_audit_path),
        PROJECT_ROOT / "docs" / "formal_acceptance_package_audit.md",
        Path(evidence_matrix_manifest_path),
        PROJECT_ROOT / "data" / "manifests" / "formal_acceptance_evidence_matrix.csv",
        PROJECT_ROOT / "docs" / "formal_acceptance_evidence_matrix.md",
        Path(acceptance_orchestration_manifest_path),
        PROJECT_ROOT / "docs" / "review_packets" / "acceptance_review_index.md",
        Path(final_study_audit_path),
        Path(final_audit_acceptance_path),
    ]
    return "; ".join(dict.fromkeys(_display_path(path) for path in paths))


def _remaining_blockers(rows: Sequence[Mapping[str, str]]) -> list[str]:
    blockers: list[str] = []
    for row in rows:
        status = str(row.get("decision_status", ""))
        reason = str(row.get("blocking_reason", "")).strip()
        if status.startswith("blocked") and reason:
            blockers.append(reason)
    return list(dict.fromkeys(blockers))


def _string_list(value: object) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [str(item) for item in value if str(item).strip()]


def _counts(values: Iterable[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value)
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", "<br>")


__all__ = [
    "DEFAULT_ACCEPTANCE_ORCHESTRATION_MANIFEST_PATH",
    "DEFAULT_CURRENT_GOAL_COMPLETION_AUDIT_PATH",
    "DEFAULT_FINAL_AUDIT_DECISION_DOC_PATH",
    "DEFAULT_FINAL_AUDIT_DECISION_MANIFEST_PATH",
    "DEFAULT_FINAL_AUDIT_DECISION_PACKET_PATH",
    "DEFAULT_FINAL_STUDY_AUDIT_PATH",
    "DEFAULT_FORMAL_ACCEPTANCE_EVIDENCE_MATRIX_MANIFEST_PATH",
    "DEFAULT_FORMAL_ACCEPTANCE_PACKAGE_AUDIT_PATH",
    "FINAL_AUDIT_DECISION_COLUMNS",
    "FINAL_AUDIT_DECISION_SCOPE",
    "build_final_audit_decision_manifest",
    "build_final_audit_decision_markdown",
    "build_final_audit_decision_rows",
    "write_final_audit_decision_packet",
]
