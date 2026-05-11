"""Sensitivity strategy-readiness packet generation.

The sensitivity review packet summarizes Morris diagnostics. This module turns
those diagnostics into explicit pre-review readiness states without accepting
sensitivity outputs, waiving Sobol analysis, or treating scaffold results as
calibrated real-world evidence.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from src.realworld.sensitivity_acceptance import DEFAULT_SENSITIVITY_ACCEPTANCE_PATH
from src.realworld.sensitivity_review_packet import (
    DEFAULT_SENSITIVITY_REVIEW_PACKET_PATH,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SENSITIVITY_STRATEGY_READINESS_PACKET_PATH = (
    PROJECT_ROOT / "data" / "validation" / "sensitivity_strategy_readiness_packet.csv"
)
DEFAULT_SENSITIVITY_STRATEGY_READINESS_MANIFEST_PATH = (
    PROJECT_ROOT
    / "data"
    / "validation"
    / "sensitivity_strategy_readiness_manifest.json"
)
DEFAULT_SENSITIVITY_STRATEGY_READINESS_DOC_PATH = (
    PROJECT_ROOT / "docs" / "sensitivity_strategy_readiness_packet.md"
)
SENSITIVITY_STRATEGY_READINESS_SCOPE = (
    "Sensitivity strategy-readiness packet only; not sensitivity acceptance, "
    "not calibrated real-world sensitivity evidence, not a Sobol waiver, not "
    "operational routing evidence, and not publication-readiness approval."
)
SENSITIVITY_STRATEGY_READINESS_COLUMNS: tuple[str, ...] = (
    "category_id",
    "issue_category",
    "diagnostic_status",
    "affected_row_count",
    "readiness_status",
    "blocking_reason",
    "required_reviewer_action",
    "diagnostic_detail",
    "publication_use_status",
    "evidence_input_paths",
    "can_support_sensitivity_gate",
    "claim_boundary",
)


def build_sensitivity_strategy_readiness_rows(
    *,
    review_rows: Sequence[Mapping[str, str]] | None = None,
    review_packet_path: str | Path = DEFAULT_SENSITIVITY_REVIEW_PACKET_PATH,
    acceptance_path: str | Path = DEFAULT_SENSITIVITY_ACCEPTANCE_PATH,
) -> list[dict[str, str]]:
    """Return strategy-readiness rows for current sensitivity diagnostics."""

    rows = (
        list(review_rows)
        if review_rows is not None
        else _load_review_rows(review_packet_path)
    )
    readiness_rows = [_readiness_row(row) for row in rows]
    readiness_rows.append(_acceptance_requirement_row(Path(acceptance_path)))
    return readiness_rows


def write_sensitivity_strategy_readiness_packet(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_SENSITIVITY_STRATEGY_READINESS_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_SENSITIVITY_STRATEGY_READINESS_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_SENSITIVITY_STRATEGY_READINESS_DOC_PATH,
    review_packet_path: str | Path = DEFAULT_SENSITIVITY_REVIEW_PACKET_PATH,
) -> dict[str, Any]:
    """Write sensitivity strategy-readiness CSV, manifest, and Markdown."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=SENSITIVITY_STRATEGY_READINESS_COLUMNS,
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    column: str(row.get(column, ""))
                    for column in SENSITIVITY_STRATEGY_READINESS_COLUMNS
                }
            )

    summary = build_sensitivity_strategy_readiness_manifest(
        rows=rows,
        output_path=output,
        manifest_path=manifest,
        doc_path=doc,
        review_packet_path=review_packet_path,
    )
    manifest.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    doc.write_text(
        build_sensitivity_strategy_readiness_markdown(summary, rows=rows),
        encoding="utf-8",
    )
    return summary


def build_sensitivity_strategy_readiness_manifest(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_SENSITIVITY_STRATEGY_READINESS_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_SENSITIVITY_STRATEGY_READINESS_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_SENSITIVITY_STRATEGY_READINESS_DOC_PATH,
    review_packet_path: str | Path = DEFAULT_SENSITIVITY_REVIEW_PACKET_PATH,
) -> dict[str, Any]:
    """Return a conservative manifest for sensitivity readiness rows."""

    status_counts = _counts(row.get("readiness_status", "") for row in rows)
    blocking_count = sum(
        1 for row in rows if str(row.get("readiness_status", "")).startswith("blocked_")
    )
    human_review_count = sum(
        1
        for row in rows
        if str(row.get("readiness_status", "")).startswith("needs_human_review_")
    )
    return {
        "schema_version": 1,
        "claim_boundary": (
            SENSITIVITY_STRATEGY_READINESS_SCOPE
            + " This packet cannot close data/manifests/sensitivity_acceptance.json."
        ),
        "result_scope": SENSITIVITY_STRATEGY_READINESS_SCOPE,
        "row_count": len(rows),
        "readiness_status_counts": status_counts,
        "blocking_request_count": blocking_count,
        "human_review_request_count": human_review_count,
        "sensitivity_gate_closure_candidate_count": 0,
        "publication_ready": False,
        "can_mark_complete": False,
        "inputs": {
            "sensitivity_review_packet": _display_path(Path(review_packet_path)),
        },
        "outputs": {
            "csv": _display_path(Path(output_path)),
            "manifest": _display_path(Path(manifest_path)),
            "doc": _display_path(Path(doc_path)),
        },
        "review_items": [
            "review unavailable or unexplained missing Morris indices before manuscript use",
            "interpret zero mu_star rows before claiming parameter dominance or no-effect behavior",
            "resolve graph-scale scope before using reduced-graph sensitivity outputs for final claims",
            "decide whether Morris screening is sufficient or Sobol analysis is required",
            "record the final sensitivity decision only in data/manifests/sensitivity_acceptance.json",
        ],
        "remaining_blockers": _remaining_blockers(rows),
    }


def build_sensitivity_strategy_readiness_markdown(
    manifest: Mapping[str, Any],
    *,
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Return a human-readable sensitivity strategy-readiness packet."""

    lines = [
        "# Sensitivity Strategy Readiness Packet",
        "",
        str(manifest.get("claim_boundary", SENSITIVITY_STRATEGY_READINESS_SCOPE)),
        "",
        "## Verdict",
        "",
        f"- Publication ready: `{str(manifest.get('publication_ready', False)).lower()}`",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        f"- Review rows: {manifest.get('row_count', 0)}",
        f"- Blocking requests: {manifest.get('blocking_request_count', 0)}",
        f"- Human-review requests: {manifest.get('human_review_request_count', 0)}",
        f"- Status counts: `{manifest.get('readiness_status_counts', {})}`",
        "",
        "## Readiness Rows",
        "",
        "| Category | Status | Affected Rows | Required Action |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {category} | {status} | {affected} | {action} |".format(
                category=_cell(row.get("category_id", "")),
                status=_cell(row.get("readiness_status", "")),
                affected=_cell(row.get("affected_row_count", "")),
                action=_cell(row.get("required_reviewer_action", "")),
            )
        )
    lines.extend(
        [
            "",
            "## Required Reviewer Actions",
            "",
            "- Decide whether current Morris screening is enough for the accepted claim boundary or whether Sobol analysis must be run.",
            "- Resolve unavailable, missing, or non-finite Morris index handling before using sensitivity rankings in the manuscript.",
            "- Review zero `mu_star` rows as diagnostics, not as calibrated no-effect findings.",
            "- Keep sensitivity outputs in scaffold scope until graph-scale, parameter, and sensitivity acceptance records exist.",
            "- Do not create formal acceptance artifacts from this readiness packet alone.",
            "",
        ]
    )
    return "\n".join(lines)


def _readiness_row(row: Mapping[str, str]) -> dict[str, str]:
    status, reason, action = _classify(row)
    return {
        "category_id": str(row.get("category_id", "")),
        "issue_category": str(row.get("issue_category", "")),
        "diagnostic_status": str(row.get("diagnostic_status", "")),
        "affected_row_count": str(row.get("affected_row_count", "")),
        "readiness_status": status,
        "blocking_reason": reason,
        "required_reviewer_action": action,
        "diagnostic_detail": str(row.get("diagnostic_detail", "")),
        "publication_use_status": str(row.get("publication_use_status", "")),
        "evidence_input_paths": str(row.get("evidence_input_paths", "")),
        "can_support_sensitivity_gate": "false",
        "claim_boundary": SENSITIVITY_STRATEGY_READINESS_SCOPE,
    }


def _acceptance_requirement_row(acceptance_path: Path) -> dict[str, str]:
    present = acceptance_path.exists()
    return {
        "category_id": "sensitivity_acceptance_record",
        "issue_category": "Formal sensitivity acceptance record",
        "diagnostic_status": "record_present" if present else "record_absent",
        "affected_row_count": "",
        "readiness_status": (
            "needs_human_review_sensitivity_acceptance_record"
            if present
            else "blocked_missing_sensitivity_acceptance_record"
        ),
        "blocking_reason": (
            "" if present else "data/manifests/sensitivity_acceptance.json is absent"
        ),
        "required_reviewer_action": (
            "validate the existing sensitivity acceptance record"
            if present
            else "record method, graph scope, parameter-range, SALib-output, index-handling, and Sobol decisions only after review"
        ),
        "diagnostic_detail": _display_path(acceptance_path),
        "publication_use_status": "blocked_until_sensitivity_acceptance",
        "evidence_input_paths": _display_path(acceptance_path),
        "can_support_sensitivity_gate": "false",
        "claim_boundary": SENSITIVITY_STRATEGY_READINESS_SCOPE,
    }


def _classify(row: Mapping[str, str]) -> tuple[str, str, str]:
    category_id = str(row.get("category_id", ""))
    diagnostic_status = str(row.get("diagnostic_status", ""))
    affected = _int(row.get("affected_row_count"))

    if category_id == "structural_readiness":
        if diagnostic_status == "ready_for_review":
            return (
                "needs_human_review_morris_artifact_selection",
                "",
                "confirm these Morris artifacts correspond to the selected final-study sensitivity run",
            )
        return (
            "blocked_structural_sensitivity_diagnostics",
            "Morris sensitivity artifacts are not structurally ready",
            "repair or regenerate Morris artifacts before strategy review",
        )
    if category_id == "missing_or_nonfinite_morris_indices":
        if diagnostic_status == "review_required_unavailable_indices":
            return (
                "needs_human_review_unavailable_morris_indices",
                "",
                "document why the affected Morris indices are unavailable and how those rows are handled in tables and claims",
            )
        if affected > 0:
            return (
                "blocked_missing_or_nonfinite_morris_indices",
                "Morris summary contains missing or non-finite index values",
                "exclude, recalculate, or explicitly document handling for affected rows before acceptance",
            )
        return (
            "needs_human_review_index_handling",
            "",
            "confirm index handling is complete before using sensitivity rankings",
        )
    if category_id == "zero_mu_star_rows":
        if affected > 0:
            return (
                "needs_human_review_zero_mu_star_interpretation",
                "",
                "interpret zero-effect rows before claiming parameter influence or no-effect findings",
            )
        return (
            "needs_human_review_zero_mu_star_absence",
            "",
            "confirm no zero-effect rows require special manuscript handling",
        )
    if category_id == "reduced_graph_scope":
        if affected > 0 or diagnostic_status == "review_required_reduced_analysis_graph":
            return (
                "blocked_reduced_graph_scope_for_sensitivity_claims",
                "sensitivity outputs use a reduced analysis graph",
                "close graph-scale acceptance or regenerate sensitivity outputs on the accepted graph method",
            )
        return (
            "needs_human_review_sensitivity_graph_scope",
            "",
            "review graph scope before sensitivity acceptance",
        )
    if category_id == "result_scope":
        if "scaffold" in diagnostic_status or "not_calibrated" in diagnostic_status:
            return (
                "blocked_scaffold_or_not_calibrated_result_scope",
                "current sensitivity result scope is scaffold or not calibrated",
                "keep final claims bounded until sensitivity results are accepted on final evidence scope",
            )
        return (
            "needs_human_review_sensitivity_result_scope",
            "",
            "review result scope wording before manuscript use",
        )
    if category_id == "sobol_decision_requirement":
        return (
            "blocked_missing_morris_vs_sobol_decision",
            "Morris-vs-Sobol method decision is not recorded in formal acceptance",
            "decide whether Morris screening is sufficient or Sobol analysis is required",
        )
    return (
        "blocked_unclassified_sensitivity_category",
        f"unrecognized category_id {category_id!r}",
        "classify this sensitivity category before strategy review",
    )


def _remaining_blockers(rows: Sequence[Mapping[str, str]]) -> list[str]:
    blockers: list[str] = []
    for row in rows:
        status = str(row.get("readiness_status", ""))
        reason = str(row.get("blocking_reason", "")).strip()
        if status.startswith("blocked_") and reason:
            blockers.append(reason)
    return blockers


def _load_review_rows(path: str | Path) -> list[dict[str, str]]:
    packet = Path(path)
    if not packet.exists():
        return []
    with packet.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _counts(values: Sequence[str] | Any) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value)
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _int(value: object) -> int:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return 0


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", "<br>")


__all__ = [
    "DEFAULT_SENSITIVITY_STRATEGY_READINESS_DOC_PATH",
    "DEFAULT_SENSITIVITY_STRATEGY_READINESS_MANIFEST_PATH",
    "DEFAULT_SENSITIVITY_STRATEGY_READINESS_PACKET_PATH",
    "SENSITIVITY_STRATEGY_READINESS_COLUMNS",
    "SENSITIVITY_STRATEGY_READINESS_SCOPE",
    "build_sensitivity_strategy_readiness_manifest",
    "build_sensitivity_strategy_readiness_markdown",
    "build_sensitivity_strategy_readiness_rows",
    "write_sensitivity_strategy_readiness_packet",
]
