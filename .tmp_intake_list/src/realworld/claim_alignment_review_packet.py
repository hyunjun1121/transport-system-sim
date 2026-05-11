"""Manuscript/report claim-alignment review packet generation.

The manuscript gate requires claim-by-claim review against accepted evidence.
This module scans the paper draft, Korean report source, and figure/table
manifest for claim-bearing terms, classifies obvious guardrail language
separately from claim candidates, and writes reviewer artifacts. It does not
edit the manuscript and does not create ``manuscript_acceptance.json``.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
import re
from typing import Any, Iterable, Mapping, Sequence

from src.realworld.final_study_readiness import audit_final_study_readiness


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PAPER_DRAFT_PATH = PROJECT_ROOT / "paper" / "paper_draft.md"
DEFAULT_REPORT_DRAFT_PATH = PROJECT_ROOT / "report_draft.md"
DEFAULT_FIGURE_TABLE_MANIFEST_PATH = (
    PROJECT_ROOT
    / "results"
    / "realworld_pilot"
    / "tables"
    / "figure_table_manifest.json"
)
DEFAULT_CLAIM_ALIGNMENT_REVIEW_PACKET_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "claim_alignment_review_packet.csv"
)
DEFAULT_CLAIM_ALIGNMENT_REVIEW_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "claim_alignment_review_manifest.json"
)
DEFAULT_CLAIM_ALIGNMENT_REVIEW_DOC_PATH = (
    PROJECT_ROOT / "docs" / "claim_alignment_review_packet.md"
)
CLAIM_ALIGNMENT_REVIEW_SCOPE = (
    "Claim-alignment review packet only; not manuscript acceptance, not "
    "calibrated real-world validation, and not operational routing approval."
)
CLAIM_ALIGNMENT_REVIEW_COLUMNS: tuple[str, ...] = (
    "claim_id",
    "source_path",
    "line_number",
    "claim_category",
    "matched_terms",
    "excerpt",
    "gate_dependency",
    "current_gate_status",
    "review_status",
    "required_action",
    "target_acceptance_artifact",
    "can_support_manuscript_acceptance",
    "claim_boundary",
)

CLAIM_PATTERNS: tuple[tuple[str, str, str], ...] = (
    ("operational", r"\boperational(?:ly)?\b|\boperation(?:s)?\b", "operational_claim"),
    ("calibrated", r"\bcalibrat(?:ed|ion|e)\b", "calibration_claim"),
    ("validated", r"\bvalidat(?:ed|ion|e)\b", "validation_claim"),
    ("accepted", r"\baccept(?:ed|ance)?\b", "acceptance_claim"),
    ("real-world", r"\breal[- ]world\b", "real_world_claim"),
    ("proves", r"\bprov(?:e|es|ed)\b", "causal_or_superiority_claim"),
    ("superior", r"\bsuperior(?:ity)?\b|\balways superior\b", "causal_or_superiority_claim"),
    (
        "ready",
        (
            r"\b(final[- ]study|publication|study|deployment|operational)\s+ready\b"
            r"|\bready\s+for\s+(publication|deployment|operations?)\b"
            r"|\bcomplete(?:d|ly)?\b"
        ),
        "readiness_claim",
    ),
    ("publication", r"\bpublication[- ]grade\b|\bSCI[- ]grade\b", "publication_claim"),
)
INLINE_CODE_PATTERN = re.compile(r"`[^`]*`")
GUARDRAIL_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bnot\b.{0,120}\b(calibrated|operational|accepted|acceptance|validated|validation|ready|complete|proof|proves?|real[- ]world|publication[- ]grade|SCI[- ]grade|superior(?:ity)?)\b",
        r"\bno\b.{0,120}\b(formal approvals?|formal acceptance|calibrated|accepted|validation|validated|real[- ]world results?|operational)\b",
        r"\b(absent|missing|unavailable)\b.{0,120}\b(formal approvals?|formal acceptance|acceptance|approval|calibrated|validation|validated|real[- ]world results?|operational)\b",
        r"\b(calibrated|accepted|acceptance|validation|validated|real[- ]world results?|operational)\b.{0,120}\b(absent|missing|unavailable)\b",
        r"\bdoes not\b.{0,120}\b(create|replace|close|approve|support|waive|evaluate|prove|provide|contain)\b",
        r"\bis not\b.{0,120}\b(.*acceptance|.*evidence|.*calibration|.*calibrated|.*validation|.*validated|.*operational|.*approval|.*publication)\b",
        r"\bdo not\b.{0,80}\b(claim|interpret|describe|use|approve)\b",
        r"\bshould not\b.{0,80}\b(claim|interpret|describe|use|be reported)\b",
        r"\bcannot\b.{0,80}\b(accept|approve|mark|claim|support)\b",
        r"\bmust not\b.{0,80}\b(claim|interpret|describe|use|approve)\b",
        r"\bwithout\b.{0,120}\b(accepting|approving|creating|claiming|validating)\b",
        r"\brather than\b.{0,120}\b(accepted|calibrated|source-backed|evidence|approval)\b",
        r"\bshould not be described as\b",
    )
)


def build_claim_alignment_review_rows(
    *,
    paper_path: str | Path = DEFAULT_PAPER_DRAFT_PATH,
    report_path: str | Path = DEFAULT_REPORT_DRAFT_PATH,
    figure_manifest_path: str | Path = DEFAULT_FIGURE_TABLE_MANIFEST_PATH,
    final_study_audit: Mapping[str, Any] | None = None,
) -> list[dict[str, str]]:
    """Return line-level claim alignment rows for current manuscript artifacts."""

    audit = dict(final_study_audit or audit_final_study_readiness())
    gate_status = _gate_status_map(audit)
    rows: list[dict[str, str]] = []
    for source_path in (Path(paper_path), Path(report_path)):
        rows.extend(_scan_text_file(source_path, gate_status=gate_status))
    rows.extend(_figure_manifest_rows(Path(figure_manifest_path), gate_status=gate_status))
    for index, row in enumerate(rows, start=1):
        row["claim_id"] = f"claim_review_{index:04d}"
    return rows


def write_claim_alignment_review_packet(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_CLAIM_ALIGNMENT_REVIEW_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_CLAIM_ALIGNMENT_REVIEW_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_CLAIM_ALIGNMENT_REVIEW_DOC_PATH,
    paper_path: str | Path = DEFAULT_PAPER_DRAFT_PATH,
    report_path: str | Path = DEFAULT_REPORT_DRAFT_PATH,
    figure_manifest_path: str | Path = DEFAULT_FIGURE_TABLE_MANIFEST_PATH,
) -> dict[str, Any]:
    """Write CSV, JSON, and Markdown claim-alignment review artifacts."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CLAIM_ALIGNMENT_REVIEW_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: str(row.get(column, "")) for column in CLAIM_ALIGNMENT_REVIEW_COLUMNS})

    summary = build_claim_alignment_review_manifest(
        rows=rows,
        output_path=output,
        manifest_path=manifest,
        doc_path=doc,
        paper_path=paper_path,
        report_path=report_path,
        figure_manifest_path=figure_manifest_path,
    )
    manifest.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    doc.write_text(
        build_claim_alignment_review_markdown(summary, rows=rows),
        encoding="utf-8",
    )
    return summary


def build_claim_alignment_review_manifest(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_CLAIM_ALIGNMENT_REVIEW_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_CLAIM_ALIGNMENT_REVIEW_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_CLAIM_ALIGNMENT_REVIEW_DOC_PATH,
    paper_path: str | Path = DEFAULT_PAPER_DRAFT_PATH,
    report_path: str | Path = DEFAULT_REPORT_DRAFT_PATH,
    figure_manifest_path: str | Path = DEFAULT_FIGURE_TABLE_MANIFEST_PATH,
) -> dict[str, Any]:
    """Return a conservative manifest for the claim-alignment packet."""

    review_status_counts = _counts(row.get("review_status", "") for row in rows)
    category_counts = _counts(row.get("claim_category", "") for row in rows)
    source_counts = _counts(row.get("source_path", "") for row in rows)
    gate_counts = _counts(row.get("gate_dependency", "") for row in rows)
    overclaim_candidate_count = sum(
        1 for row in rows if row.get("review_status") == "requires_revision_or_acceptance"
    )
    guardrail_count = sum(
        1 for row in rows if row.get("review_status") == "guardrail_language"
    )
    return {
        "schema_version": 1,
        "claim_boundary": (
            CLAIM_ALIGNMENT_REVIEW_SCOPE
            + " A reviewer must still create data/manifests/manuscript_acceptance.json "
            "after evidence gates and result claims are reviewed."
        ),
        "result_scope": CLAIM_ALIGNMENT_REVIEW_SCOPE,
        "row_count": len(rows),
        "source_counts": source_counts,
        "claim_category_counts": category_counts,
        "gate_dependency_counts": gate_counts,
        "review_status_counts": review_status_counts,
        "overclaim_candidate_count": overclaim_candidate_count,
        "guardrail_language_count": guardrail_count,
        "publication_ready": False,
        "can_mark_complete": False,
        "inputs": {
            "paper_draft": _display_path(Path(paper_path)),
            "report_draft": _display_path(Path(report_path)),
            "figure_table_manifest": _display_path(Path(figure_manifest_path)),
        },
        "outputs": {
            "csv": _display_path(Path(output_path)),
            "manifest": _display_path(Path(manifest_path)),
            "doc": _display_path(Path(doc_path)),
        },
        "review_items": [
            "review all non-guardrail real-world, calibrated, validated, accepted, operational, and superiority language",
            "keep figure/table captions within scaffold-only claim boundaries until acceptance gates close",
            "revise Korean report text after fixing encoding/readability issues before formal manuscript acceptance",
            "create data/manifests/manuscript_acceptance.json only after claim-by-claim review",
        ],
        "remaining_blockers": [
            "formal manuscript/report acceptance record is absent",
            "claim-alignment rows are review aids and do not approve manuscript claims",
            "evidence gates remain blocked, so result claims cannot be accepted as final-study claims",
        ],
    }


def build_claim_alignment_review_markdown(
    manifest: Mapping[str, Any],
    *,
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Return a human-readable claim-alignment review packet."""

    lines = [
        "# Claim Alignment Review Packet",
        "",
        str(manifest.get("claim_boundary", CLAIM_ALIGNMENT_REVIEW_SCOPE)),
        "",
        "## Verdict",
        "",
        f"- Publication ready: `{str(manifest.get('publication_ready', False)).lower()}`",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        f"- Claim rows: {manifest.get('row_count', 0)}",
        f"- Overclaim candidates: {manifest.get('overclaim_candidate_count', 0)}",
        f"- Guardrail rows: {manifest.get('guardrail_language_count', 0)}",
        "",
        "## Review Rows",
        "",
        "| Claim | Source | Category | Status | Required Action |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows[:80]:
        lines.append(
            "| {claim} | {source}:{line} | {category} | {status} | {action} |".format(
                claim=_cell(row.get("claim_id", "")),
                source=_cell(row.get("source_path", "")),
                line=_cell(row.get("line_number", "")),
                category=_cell(row.get("claim_category", "")),
                status=_cell(row.get("review_status", "")),
                action=_cell(row.get("required_action", "")),
            )
        )
    if len(rows) > 80:
        lines.append(
            f"| ... | ... | ... | ... | {len(rows) - 80} additional rows in CSV |"
        )
    lines.extend(
        [
            "",
            "## Required Reviewer Actions",
            "",
            "- Review every `requires_revision_or_acceptance` row before manuscript acceptance.",
            "- Keep guardrail rows if they correctly prevent overclaiming.",
            "- Check figure/table manifest boundaries against accepted evidence gates.",
            "- Create `data/manifests/manuscript_acceptance.json` only after evidence gates and claims align.",
            "",
        ]
    )
    return "\n".join(lines)


def _scan_text_file(
    source_path: Path,
    *,
    gate_status: Mapping[str, str],
) -> list[dict[str, str]]:
    if not source_path.exists():
        return [
            _row(
                source_path=source_path,
                line_number=0,
                claim_category="missing_artifact",
                matched_terms="missing",
                excerpt="",
                gate_dependency="manuscript_report_alignment",
                current_gate_status=gate_status.get("manuscript_report_alignment", "blocked"),
                review_status="requires_revision_or_acceptance",
                required_action="restore or explicitly remove missing manuscript artifact from acceptance scope",
            )
        ]
    text = source_path.read_text(encoding="utf-8", errors="replace")
    rows: list[dict[str, str]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        matches = _line_matches(line)
        if not matches:
            continue
        category = _dominant_category(matches)
        gate_dependency = _gate_for_category(category)
        guarded = _is_guardrail_line(line)
        rows.append(
            _row(
                source_path=source_path,
                line_number=line_number,
                claim_category=category,
                matched_terms=";".join(term for term, _category in matches),
                excerpt=_excerpt(line),
                gate_dependency=gate_dependency,
                current_gate_status=gate_status.get(gate_dependency, "blocked"),
                review_status=(
                    "guardrail_language" if guarded else "requires_revision_or_acceptance"
                ),
                required_action=_required_action(category, guarded),
            )
        )
    return rows


def _figure_manifest_rows(
    manifest_path: Path,
    *,
    gate_status: Mapping[str, str],
) -> list[dict[str, str]]:
    if not manifest_path.exists():
        return []
    value = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows: list[dict[str, str]] = []
    for key in ("claim_boundary", "result_scope"):
        text = str(value.get(key, ""))
        if text:
            rows.append(
                _row(
                    source_path=manifest_path,
                    line_number=0,
                    claim_category="figure_table_boundary",
                    matched_terms="figure_table_manifest",
                    excerpt=_excerpt(text),
                    gate_dependency="manuscript_report_alignment",
                    current_gate_status=gate_status.get("manuscript_report_alignment", "blocked"),
                    review_status="guardrail_language" if _is_guardrail_line(text) else "requires_revision_or_acceptance",
                    required_action=(
                        "verify figure/table boundary language before manuscript acceptance"
                    ),
                )
            )
    figures = value.get("figures", {})
    if isinstance(figures, Mapping):
        for figure_id, figure in figures.items():
            if not isinstance(figure, Mapping):
                continue
            caption = str(figure.get("caption_note", ""))
            if not caption:
                continue
            rows.append(
                _row(
                    source_path=manifest_path,
                    line_number=0,
                    claim_category="figure_caption_boundary",
                    matched_terms=str(figure_id),
                    excerpt=_excerpt(caption),
                    gate_dependency="manuscript_report_alignment",
                    current_gate_status=gate_status.get("manuscript_report_alignment", "blocked"),
                    review_status="guardrail_language" if _is_guardrail_line(caption) else "requires_revision_or_acceptance",
                    required_action="verify figure caption remains scaffold-only until evidence gates close",
                )
            )
    return rows


def _row(
    *,
    source_path: Path,
    line_number: int,
    claim_category: str,
    matched_terms: str,
    excerpt: str,
    gate_dependency: str,
    current_gate_status: str,
    review_status: str,
    required_action: str,
) -> dict[str, str]:
    return {
        "claim_id": "",
        "source_path": _display_path(source_path),
        "line_number": str(line_number),
        "claim_category": claim_category,
        "matched_terms": matched_terms,
        "excerpt": excerpt,
        "gate_dependency": gate_dependency,
        "current_gate_status": current_gate_status,
        "review_status": review_status,
        "required_action": required_action,
        "target_acceptance_artifact": "data/manifests/manuscript_acceptance.json",
        "can_support_manuscript_acceptance": "false",
        "claim_boundary": CLAIM_ALIGNMENT_REVIEW_SCOPE,
    }


def _line_matches(line: str) -> list[tuple[str, str]]:
    scan_text = _claim_scan_text(line)
    matches: list[tuple[str, str]] = []
    for term, pattern, category in CLAIM_PATTERNS:
        if re.search(pattern, scan_text, flags=re.IGNORECASE):
            matches.append((term, category))
    return matches


def _claim_scan_text(line: str) -> str:
    return INLINE_CODE_PATTERN.sub("", line)


def _dominant_category(matches: Sequence[tuple[str, str]]) -> str:
    categories = [category for _term, category in matches]
    for preferred in (
        "operational_claim",
        "calibration_claim",
        "validation_claim",
        "acceptance_claim",
        "causal_or_superiority_claim",
        "real_world_claim",
        "readiness_claim",
        "publication_claim",
    ):
        if preferred in categories:
            return preferred
    return categories[0] if categories else "claim"


def _gate_for_category(category: str) -> str:
    if category == "calibration_claim":
        return "parameter_evidence"
    if category == "validation_claim":
        return "validation_package"
    if category == "acceptance_claim":
        return "final_audit"
    if category == "publication_claim":
        return "manuscript_report_alignment"
    return "manuscript_report_alignment"


def _required_action(category: str, guarded: bool) -> str:
    if guarded:
        return "verify this guardrail language remains accurate and does not imply acceptance"
    if category == "calibration_claim":
        return "revise or hold calibration language until parameter, road, rail, and validation gates close"
    if category == "validation_claim":
        return "revise or hold validation language until validation acceptance exists"
    if category == "acceptance_claim":
        return "revise or hold acceptance/finality language until formal acceptance records exist"
    if category == "operational_claim":
        return "revise operational language to decision-support framing unless formal scope allows it"
    if category == "causal_or_superiority_claim":
        return "replace proof/superiority language with conditional regime language"
    return "review claim against current evidence gates before manuscript acceptance"


def _is_guardrail_line(line: str) -> bool:
    return any(pattern.search(line) for pattern in GUARDRAIL_PATTERNS)


def _gate_status_map(audit: Mapping[str, Any]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for gate in audit.get("gates", []):
        if not isinstance(gate, Mapping):
            continue
        gate_id = str(gate.get("gate_id", ""))
        if gate_id:
            mapping[gate_id] = "ready" if gate.get("ready") else "blocked"
    return mapping


def _counts(values: Iterable[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value)
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _excerpt(line: str) -> str:
    clean = " ".join(str(line).strip().split())
    return clean[:240]


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", "<br>")


__all__ = [
    "CLAIM_ALIGNMENT_REVIEW_COLUMNS",
    "CLAIM_ALIGNMENT_REVIEW_SCOPE",
    "DEFAULT_CLAIM_ALIGNMENT_REVIEW_DOC_PATH",
    "DEFAULT_CLAIM_ALIGNMENT_REVIEW_MANIFEST_PATH",
    "DEFAULT_CLAIM_ALIGNMENT_REVIEW_PACKET_PATH",
    "build_claim_alignment_review_manifest",
    "build_claim_alignment_review_markdown",
    "build_claim_alignment_review_rows",
    "write_claim_alignment_review_packet",
]
