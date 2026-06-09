"""Focused manuscript/report decision worksheet.

The claim-alignment and figure/table packets expose detailed manuscript review
work. This module turns their current state into manuscript/report gate
decision rows without creating ``data/manifests/manuscript_acceptance.json`` or
approving release-scope study claims.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from src.realworld.claim_alignment_review_packet import (
    DEFAULT_CLAIM_ALIGNMENT_REVIEW_MANIFEST_PATH,
    DEFAULT_CLAIM_ALIGNMENT_REVIEW_PACKET_PATH,
)
from src.realworld.figure_table_review_packet import (
    DEFAULT_FIGURE_TABLE_REVIEW_MANIFEST_PATH,
    DEFAULT_FIGURE_TABLE_REVIEW_PACKET_PATH,
)
from src.realworld.manuscript_acceptance import DEFAULT_MANUSCRIPT_ACCEPTANCE_PATH


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PAPER_DRAFT_PATH = PROJECT_ROOT / "paper" / "paper_draft.md"
DEFAULT_REPORT_DRAFT_PATH = PROJECT_ROOT / "report_draft.md"
DEFAULT_REPORT_DOCX_PATH = PROJECT_ROOT / "report.docx"
DEFAULT_FIGURE_TABLE_MANIFEST_PATH = (
    PROJECT_ROOT
    / "results"
    / "realworld_pilot"
    / "tables"
    / "figure_table_manifest.json"
)
DEFAULT_MANUSCRIPT_REPORT_DECISION_PACKET_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "manuscript_report_decision_packet.csv"
)
DEFAULT_MANUSCRIPT_REPORT_DECISION_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "manuscript_report_decision_manifest.json"
)
DEFAULT_MANUSCRIPT_REPORT_DECISION_DOC_PATH = (
    PROJECT_ROOT / "docs" / "manuscript_report_decision_packet.md"
)
MANUSCRIPT_REPORT_DECISION_SCOPE = (
    "Manuscript/report decision packet only; not manuscript acceptance, not "
    "evidence-gate acceptance, not calibrated real-world validation, and not "
    "operational routing approval."
)
MANUSCRIPT_REPORT_DECISION_COLUMNS: tuple[str, ...] = (
    "decision_id",
    "decision_topic",
    "candidate_decision",
    "current_evidence",
    "decision_status",
    "blocking_reason",
    "required_reviewer_action",
    "followup_artifacts",
    "evidence_input_paths",
    "can_support_manuscript_acceptance",
    "claim_boundary",
)

UPSTREAM_EVIDENCE_GATE_IDS: tuple[str, ...] = (
    "pilot_region_accepted",
    "cached_osm_input",
    "graph_scale_strategy",
    "data_provenance",
    "parameter_evidence",
    "rail_evidence",
    "validation_package",
    "sensitivity_analysis",
    "full_experiment_output",
)


def build_manuscript_report_decision_rows(
    *,
    paper_path: str | Path = DEFAULT_PAPER_DRAFT_PATH,
    report_path: str | Path = DEFAULT_REPORT_DRAFT_PATH,
    report_docx_path: str | Path = DEFAULT_REPORT_DOCX_PATH,
    figure_manifest_path: str | Path = DEFAULT_FIGURE_TABLE_MANIFEST_PATH,
    claim_alignment_manifest_path: str
    | Path = DEFAULT_CLAIM_ALIGNMENT_REVIEW_MANIFEST_PATH,
    figure_table_review_manifest_path: str
    | Path = DEFAULT_FIGURE_TABLE_REVIEW_MANIFEST_PATH,
    manuscript_acceptance_path: str | Path = DEFAULT_MANUSCRIPT_ACCEPTANCE_PATH,
    final_study_audit: Mapping[str, Any] | None = None,
) -> list[dict[str, str]]:
    """Return reviewer rows for manuscript/report gate decisions."""

    paper = Path(paper_path)
    report = Path(report_path)
    docx = Path(report_docx_path)
    figure_manifest = _read_json_object(figure_manifest_path)
    claim_manifest = _read_json_object(claim_alignment_manifest_path)
    figure_review_manifest = _read_json_object(figure_table_review_manifest_path)
    acceptance_path = Path(manuscript_acceptance_path)
    if final_study_audit is None:
        from src.realworld.final_study_readiness import audit_final_study_readiness

        audit = dict(audit_final_study_readiness())
    else:
        audit = dict(final_study_audit)
    blocked_upstream_gates = _blocked_upstream_gate_ids(audit)
    overclaim_count = _int(claim_manifest.get("overclaim_candidate_count"))
    figure_blocking_count = _int(figure_review_manifest.get("blocking_review_count"))
    figure_human_count = _int(figure_review_manifest.get("human_review_count"))
    figure_scope = str(figure_manifest.get("result_scope", "")).strip()
    evidence_paths = _evidence_paths(
        paper_path=paper,
        report_path=report,
        report_docx_path=docx,
        figure_manifest_path=figure_manifest_path,
        claim_alignment_manifest_path=claim_alignment_manifest_path,
        figure_table_review_manifest_path=figure_table_review_manifest_path,
    )

    return [
        _row(
            decision_id="paper_claim_review_decision",
            decision_topic="English paper claim review",
            candidate_decision=(
                "Retain the current paper draft only after every non-guardrail "
                "claim row is reviewed, revised, or explicitly retained within "
                "the scaffold claim boundary"
            ),
            current_evidence=_text_evidence(
                label="paper",
                path=paper,
                claim_manifest=claim_manifest,
            ),
            decision_status="needs_human_review_paper_claims",
            blocking_reason="",
            required_reviewer_action=(
                "Review paper claim rows and revise any language that implies "
                "unsupported evidence-verification, benchmark treatment, "
                "route-command use, or release-complete wording."
            ),
            followup_artifacts=(
                "paper/paper_draft.md; "
                "data/manifests/manuscript_acceptance.json"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            decision_id="korean_report_review_decision",
            decision_topic="Korean report source review",
            candidate_decision=(
                "Retain the Korean report source and generated docx only after "
                "review confirms readability, claim scope, and consistency with "
                "reviewed upstream evidence decisions"
            ),
            current_evidence=_text_evidence(
                label="report",
                path=report,
                claim_manifest=claim_manifest,
            ),
            decision_status=(
                "blocked_missing_report_source"
                if not report.exists()
                else "needs_human_review_korean_report_scope"
            ),
            blocking_reason=(
                "report_draft.md is absent" if not report.exists() else ""
            ),
            required_reviewer_action=(
                "Review Korean report text against current scaffold limitations "
                "and regenerate the docx only after reviewed manuscript changes."
            ),
            followup_artifacts="report_draft.md; report.docx",
            evidence_input_paths=evidence_paths,
        ),
        _row(
            decision_id="figure_table_use_decision",
            decision_topic="Figure/table use in manuscript claims",
            candidate_decision=(
                "Use current figures and tables only as scaffold evidence until "
                "graph-scale, experiment, validation, and sensitivity dependencies "
                "have reviewer decision records"
            ),
            current_evidence=_figure_review_evidence(
                figure_manifest=figure_manifest,
                figure_review_manifest=figure_review_manifest,
            ),
            decision_status=(
                "blocked_figure_table_review_dependency"
                if figure_blocking_count
                else "needs_human_review_figure_table_use"
            ),
            blocking_reason=(
                "; ".join(_list_value(figure_review_manifest, "remaining_blockers"))
                if figure_blocking_count
                else ""
            ),
            required_reviewer_action=(
                "Resolve figure/table blocker rows and keep captions in scaffold "
                "scope until a formal manuscript decision record exists."
            ),
            followup_artifacts=(
                "data/manifests/figure_table_review_packet.csv; "
                "data/manifests/manuscript_acceptance.json"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            decision_id="result_claim_alignment_decision",
            decision_topic="Result-claim alignment",
            candidate_decision=(
                "Retain result claims only after non-guardrail claim rows are "
                "reviewed and aligned with upstream evidence decisions"
            ),
            current_evidence=_claim_alignment_evidence(claim_manifest),
            decision_status=(
                "blocked_claim_alignment_review_dependency"
                if overclaim_count
                else "needs_human_review_claim_alignment"
            ),
            blocking_reason=(
                f"claim-alignment packet has {overclaim_count} rows requiring revision or explicit retention"
                if overclaim_count
                else ""
            ),
            required_reviewer_action=(
                "Review or revise every overclaim candidate before recording "
                "result_claims_aligned in a manuscript decision record."
            ),
            followup_artifacts=(
                "data/manifests/claim_alignment_review_packet.csv; "
                "data/manifests/manuscript_acceptance.json"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            decision_id="upstream_evidence_gate_dependency",
            decision_topic="Upstream evidence-gate dependency",
            candidate_decision=(
                "Move manuscript/report claims out of scaffold scope only after "
                "pilot, provenance, graph-scale, input-evidence, validation, "
                "sensitivity, and experiment gates close"
            ),
            current_evidence=_upstream_gate_evidence(
                audit=audit,
                blocked_gate_ids=blocked_upstream_gates,
            ),
            decision_status=(
                "blocked_upstream_evidence_gate_dependency"
                if blocked_upstream_gates
                else "needs_human_review_upstream_gate_scope"
            ),
            blocking_reason=(
                "upstream evidence gates blocked: " + ", ".join(blocked_upstream_gates)
                if blocked_upstream_gates
                else ""
            ),
            required_reviewer_action=(
                "Keep manuscript/report result language in scaffold scope until "
                "the upstream evidence gates are reviewed or explicitly limited."
            ),
            followup_artifacts=(
                "data/manifests/graph_scale_acceptance.json; "
                "data/manifests/validation_acceptance.json; "
                "data/manifests/experiment_acceptance.json; "
                "data/manifests/manuscript_acceptance.json"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            decision_id="docx_regeneration_decision",
            decision_topic="Generated report.docx review",
            candidate_decision=(
                "Treat report.docx as regenerated only after reviewer confirms it "
                "matches the reviewed report source and current figure/table scope"
            ),
            current_evidence=_docx_evidence(docx, report=report),
            decision_status=(
                "needs_human_review_docx_regeneration"
                if docx.exists()
                else "blocked_missing_report_docx"
            ),
            blocking_reason=(
                "" if docx.exists() else "report.docx is absent"
            ),
            required_reviewer_action=(
                "Regenerate and review report.docx after any reviewed report "
                "or figure/table changes."
            ),
            followup_artifacts="report.docx; generate_report.py",
            evidence_input_paths=evidence_paths,
        ),
        _row(
            decision_id="formal_manuscript_acceptance_boundary",
            decision_topic="Formal manuscript acceptance boundary",
            candidate_decision=(
                "Create manuscript_acceptance.json only after paper, Korean "
                "report, docx, figure/table, evidence-gate, and result-claim "
                "review decisions are complete"
            ),
            current_evidence=(
                f"manuscript_acceptance_present={str(acceptance_path.exists()).lower()}"
            ),
            decision_status=(
                "needs_human_review_formal_manuscript_acceptance"
                if acceptance_path.exists()
                else "blocked_missing_manuscript_acceptance_record"
            ),
            blocking_reason=(
                ""
                if acceptance_path.exists()
                else "data/manifests/manuscript_acceptance.json is absent"
            ),
            required_reviewer_action=(
                "Record a formal manuscript decision only after placeholders are "
                "removed and source-backed evidence decisions support the claims."
            ),
            followup_artifacts="data/manifests/manuscript_acceptance.json",
            evidence_input_paths=evidence_paths,
        ),
    ]


def write_manuscript_report_decision_packet(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_MANUSCRIPT_REPORT_DECISION_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_MANUSCRIPT_REPORT_DECISION_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_MANUSCRIPT_REPORT_DECISION_DOC_PATH,
    paper_path: str | Path = DEFAULT_PAPER_DRAFT_PATH,
    report_path: str | Path = DEFAULT_REPORT_DRAFT_PATH,
    report_docx_path: str | Path = DEFAULT_REPORT_DOCX_PATH,
    figure_manifest_path: str | Path = DEFAULT_FIGURE_TABLE_MANIFEST_PATH,
    claim_alignment_manifest_path: str
    | Path = DEFAULT_CLAIM_ALIGNMENT_REVIEW_MANIFEST_PATH,
    figure_table_review_manifest_path: str
    | Path = DEFAULT_FIGURE_TABLE_REVIEW_MANIFEST_PATH,
) -> dict[str, Any]:
    """Write CSV, JSON, and Markdown manuscript/report decision artifacts."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=MANUSCRIPT_REPORT_DECISION_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    column: str(row.get(column, ""))
                    for column in MANUSCRIPT_REPORT_DECISION_COLUMNS
                }
            )

    summary = build_manuscript_report_decision_manifest(
        rows=rows,
        output_path=output,
        manifest_path=manifest,
        doc_path=doc,
        paper_path=paper_path,
        report_path=report_path,
        report_docx_path=report_docx_path,
        figure_manifest_path=figure_manifest_path,
        claim_alignment_manifest_path=claim_alignment_manifest_path,
        figure_table_review_manifest_path=figure_table_review_manifest_path,
    )
    manifest.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    doc.write_text(
        build_manuscript_report_decision_markdown(summary, rows=rows),
        encoding="utf-8",
    )
    return summary


def build_manuscript_report_decision_manifest(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_MANUSCRIPT_REPORT_DECISION_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_MANUSCRIPT_REPORT_DECISION_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_MANUSCRIPT_REPORT_DECISION_DOC_PATH,
    paper_path: str | Path = DEFAULT_PAPER_DRAFT_PATH,
    report_path: str | Path = DEFAULT_REPORT_DRAFT_PATH,
    report_docx_path: str | Path = DEFAULT_REPORT_DOCX_PATH,
    figure_manifest_path: str | Path = DEFAULT_FIGURE_TABLE_MANIFEST_PATH,
    claim_alignment_manifest_path: str
    | Path = DEFAULT_CLAIM_ALIGNMENT_REVIEW_MANIFEST_PATH,
    figure_table_review_manifest_path: str
    | Path = DEFAULT_FIGURE_TABLE_REVIEW_MANIFEST_PATH,
) -> dict[str, Any]:
    """Return a conservative manuscript/report decision manifest."""

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
            MANUSCRIPT_REPORT_DECISION_SCOPE
            + " It cannot create or replace data/manifests/manuscript_acceptance.json."
        ),
        "result_scope": MANUSCRIPT_REPORT_DECISION_SCOPE,
        "row_count": len(rows),
        "decision_status_counts": statuses,
        "blocking_decision_count": blocking_count,
        "human_review_decision_count": human_count,
        "paper_review_decision_recorded": False,
        "korean_report_review_decision_recorded": False,
        "docx_regeneration_decision_recorded": False,
        "figure_table_decision_recorded": False,
        "result_claims_aligned": False,
        "manuscript_acceptance_record_present": Path(
            DEFAULT_MANUSCRIPT_ACCEPTANCE_PATH
        ).exists(),
        "manuscript_gate_closure_candidate_count": 0,
        "publication_ready": False,
        "can_mark_complete": False,
        "inputs": {
            "paper_draft": _display_path(Path(paper_path)),
            "report_draft": _display_path(Path(report_path)),
            "report_docx": _display_path(Path(report_docx_path)),
            "figure_table_manifest": _display_path(Path(figure_manifest_path)),
            "claim_alignment_manifest": _display_path(
                Path(claim_alignment_manifest_path)
            ),
            "figure_table_review_manifest": _display_path(
                Path(figure_table_review_manifest_path)
            ),
        },
        "outputs": {
            "csv": _display_path(Path(output_path)),
            "manifest": _display_path(Path(manifest_path)),
            "doc": _display_path(Path(doc_path)),
        },
        "review_items": [
            "review paper and Korean report claims against evidence-gate status",
            "resolve figure/table blocker rows before release-scope manuscript claims",
            "revise or explicitly retain non-guardrail claim-alignment rows",
            "confirm report.docx is regenerated from the reviewed report source",
            "create data/manifests/manuscript_acceptance.json only after all manuscript/report decisions are source-backed",
        ],
        "remaining_blockers": _remaining_blockers(rows),
    }


def build_manuscript_report_decision_markdown(
    manifest: Mapping[str, Any],
    *,
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Return a human-readable manuscript/report decision packet."""

    lines = [
        "# Manuscript/Report Decision Packet",
        "",
        str(manifest.get("claim_boundary", MANUSCRIPT_REPORT_DECISION_SCOPE)),
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
            "- This packet does not approve paper, report, docx, figure, or table claims.",
            "- It does not replace pilot, provenance, graph-scale, input-evidence, validation, sensitivity, experiment, or manuscript acceptance.",
            "- Keep manuscript/report claims in scaffold scope until a formal manuscript decision record is reviewed.",
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
        "can_support_manuscript_acceptance": "false",
        "claim_boundary": MANUSCRIPT_REPORT_DECISION_SCOPE,
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


def _text_evidence(
    *,
    label: str,
    path: Path,
    claim_manifest: Mapping[str, Any],
) -> str:
    stats = _text_stats(path)
    source_counts = _dict_value(claim_manifest, "source_counts")
    return (
        f"{label}_present={str(stats['present']).lower()}; "
        f"{label}_line_count={stats['line_count']}; "
        f"{label}_claim_rows={source_counts.get(_display_path(path), 0)}; "
        f"overclaim_candidate_count={claim_manifest.get('overclaim_candidate_count', 0)}; "
        f"guardrail_language_count={claim_manifest.get('guardrail_language_count', 0)}"
    )


def _figure_review_evidence(
    *,
    figure_manifest: Mapping[str, Any],
    figure_review_manifest: Mapping[str, Any],
) -> str:
    figures = _dict_value(figure_manifest, "figures")
    tables = _dict_value(figure_manifest, "tables")
    return (
        f"figures={len(figures)}; tables={len(tables)}; "
        f"result_scope={figure_manifest.get('result_scope', '')}; "
        f"blocking_review_count={figure_review_manifest.get('blocking_review_count', 0)}; "
        f"human_review_count={figure_review_manifest.get('human_review_count', 0)}"
    )


def _claim_alignment_evidence(claim_manifest: Mapping[str, Any]) -> str:
    return (
        f"claim_rows={claim_manifest.get('row_count', 0)}; "
        f"overclaim_candidate_count={claim_manifest.get('overclaim_candidate_count', 0)}; "
        f"guardrail_language_count={claim_manifest.get('guardrail_language_count', 0)}; "
        f"review_status_counts={claim_manifest.get('review_status_counts', {})}"
    )


def _upstream_gate_evidence(
    *,
    audit: Mapping[str, Any],
    blocked_gate_ids: Sequence[str],
) -> str:
    return (
        f"ready_gate_count={audit.get('ready_gate_count', 0)}; "
        f"blocked_gate_count={audit.get('blocked_gate_count', 0)}; "
        f"blocked_upstream_gates={','.join(blocked_gate_ids)}"
    )


def _docx_evidence(path: Path, *, report: Path) -> str:
    size = path.stat().st_size if path.exists() else 0
    report_size = report.stat().st_size if report.exists() else 0
    return (
        f"report_docx_present={str(path.exists()).lower()}; "
        f"report_docx_size_bytes={size}; "
        f"report_source_present={str(report.exists()).lower()}; "
        f"report_source_size_bytes={report_size}"
    )


def _text_stats(path: Path) -> dict[str, int | bool]:
    if not path.exists():
        return {"present": False, "line_count": 0}
    text = path.read_text(encoding="utf-8", errors="replace")
    return {"present": True, "line_count": len(text.splitlines())}


def _blocked_upstream_gate_ids(audit: Mapping[str, Any]) -> list[str]:
    gates = audit.get("gates", [])
    blocked: list[str] = []
    if not isinstance(gates, Sequence) or isinstance(gates, (str, bytes)):
        return blocked
    for gate in gates:
        if not isinstance(gate, Mapping):
            continue
        gate_id = str(gate.get("gate_id", ""))
        if gate_id in UPSTREAM_EVIDENCE_GATE_IDS and not gate.get("ready"):
            blocked.append(gate_id)
    return blocked


def _evidence_paths(
    *,
    paper_path: str | Path,
    report_path: str | Path,
    report_docx_path: str | Path,
    figure_manifest_path: str | Path,
    claim_alignment_manifest_path: str | Path,
    figure_table_review_manifest_path: str | Path,
) -> str:
    paths = [
        Path(paper_path),
        Path(report_path),
        Path(report_docx_path),
        Path(figure_manifest_path),
        DEFAULT_CLAIM_ALIGNMENT_REVIEW_PACKET_PATH,
        Path(claim_alignment_manifest_path),
        DEFAULT_FIGURE_TABLE_REVIEW_PACKET_PATH,
        Path(figure_table_review_manifest_path),
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


def _dict_value(mapping: Mapping[str, Any], key: str) -> dict[str, Any]:
    value = mapping.get(key, {})
    if isinstance(value, Mapping):
        return dict(value)
    return {}


def _list_value(mapping: Mapping[str, Any], key: str) -> list[str]:
    value = mapping.get(key, [])
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [str(item) for item in value]


def _int(value: object) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return 0


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
    "DEFAULT_FIGURE_TABLE_MANIFEST_PATH",
    "DEFAULT_MANUSCRIPT_REPORT_DECISION_DOC_PATH",
    "DEFAULT_MANUSCRIPT_REPORT_DECISION_MANIFEST_PATH",
    "DEFAULT_MANUSCRIPT_REPORT_DECISION_PACKET_PATH",
    "DEFAULT_PAPER_DRAFT_PATH",
    "DEFAULT_REPORT_DOCX_PATH",
    "DEFAULT_REPORT_DRAFT_PATH",
    "MANUSCRIPT_REPORT_DECISION_COLUMNS",
    "MANUSCRIPT_REPORT_DECISION_SCOPE",
    "UPSTREAM_EVIDENCE_GATE_IDS",
    "build_manuscript_report_decision_manifest",
    "build_manuscript_report_decision_markdown",
    "build_manuscript_report_decision_rows",
    "write_manuscript_report_decision_packet",
]
