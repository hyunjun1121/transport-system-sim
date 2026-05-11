"""Reviewer-facing packet for current Morris sensitivity diagnostics.

This module converts the existing Morris diagnostic audit into a compact CSV
worksheet and JSON manifest. It supports final-study review, but it is not a
sensitivity acceptance record and does not make calibrated result claims.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from src.realworld.sensitivity import (
    DEFAULT_MORRIS_MANIFEST_PATH,
    DEFAULT_MORRIS_SUMMARY_PATH,
)
from src.realworld.sensitivity_diagnostics import (
    MORRIS_INDEX_COLUMNS,
    audit_morris_sensitivity_diagnostics,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SENSITIVITY_REVIEW_PACKET_PATH = (
    PROJECT_ROOT / "data" / "validation" / "sensitivity_review_packet.csv"
)
DEFAULT_SENSITIVITY_REVIEW_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "validation" / "sensitivity_review_manifest.json"
)
SENSITIVITY_REVIEW_PACKET_SCOPE = (
    "sensitivity_review_packet_not_sensitivity_acceptance"
)
SENSITIVITY_REVIEW_COLUMNS: tuple[str, ...] = (
    "category_id",
    "issue_category",
    "diagnostic_status",
    "affected_row_count",
    "diagnostic_detail",
    "review_required",
    "acceptance_ready",
    "publication_ready",
    "review_action",
    "publication_use_status",
    "evidence_input_paths",
    "claim_boundary",
)


def build_sensitivity_review_rows(
    *,
    summary_path: str | Path = DEFAULT_MORRIS_SUMMARY_PATH,
    morris_manifest_path: str | Path = DEFAULT_MORRIS_MANIFEST_PATH,
) -> list[dict[str, str]]:
    """Return conservative sensitivity-review rows from Morris diagnostics."""

    diagnostics = audit_morris_sensitivity_diagnostics(
        summary_path=summary_path,
        manifest_path=morris_manifest_path,
    )
    morris_manifest = _load_json_object(morris_manifest_path)
    evidence_paths = _evidence_path_text(summary_path, morris_manifest_path)

    return [
        _structural_readiness_row(diagnostics, evidence_paths),
        _index_issue_row(diagnostics, evidence_paths),
        _zero_mu_star_row(diagnostics, evidence_paths),
        _reduced_graph_scope_row(diagnostics, morris_manifest, evidence_paths),
        _result_scope_row(diagnostics, evidence_paths),
        _sobol_decision_row(diagnostics, morris_manifest, evidence_paths),
    ]


def write_sensitivity_review_packet(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_SENSITIVITY_REVIEW_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_SENSITIVITY_REVIEW_MANIFEST_PATH,
    summary_path: str | Path = DEFAULT_MORRIS_SUMMARY_PATH,
    morris_manifest_path: str | Path = DEFAULT_MORRIS_MANIFEST_PATH,
) -> dict[str, Any]:
    """Write the sensitivity review worksheet and non-acceptance manifest."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=SENSITIVITY_REVIEW_COLUMNS,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)

    diagnostics = audit_morris_sensitivity_diagnostics(
        summary_path=summary_path,
        manifest_path=morris_manifest_path,
    )
    value = {
        "schema_version": 1,
        "result_scope": SENSITIVITY_REVIEW_PACKET_SCOPE,
        "evidence_input_paths": {
            "morris_summary": _display_path(summary_path),
            "morris_manifest": _display_path(morris_manifest_path),
        },
        "outputs": {
            "sensitivity_review_packet": _display_path(output),
            "manifest": _display_path(manifest),
        },
        "row_count": len(rows),
        "category_ids": [str(row.get("category_id", "")) for row in rows],
        "diagnostics_ready": bool(diagnostics.get("diagnostics_ready", False)),
        "morris_summary_row_count": int(diagnostics.get("row_count", 0)),
        "rows_with_index_issues": int(
            diagnostics.get("rows_with_index_issues", 0)
        ),
        "all_rows_with_index_issues": int(
            diagnostics.get("all_rows_with_index_issues", 0)
        ),
        "unavailable_index_row_count": int(
            diagnostics.get("unavailable_index_row_count", 0)
        ),
        "unavailable_index_status_counts": dict(
            diagnostics.get("unavailable_index_status_counts", {})
        ),
        "zero_mu_star_count": int(diagnostics.get("zero_mu_star_count", 0)),
        "index_issue_counts": dict(diagnostics.get("index_issue_counts", {})),
        "all_index_issue_counts": dict(
            diagnostics.get("all_index_issue_counts", {})
        ),
        "analysis_graph_reduced": bool(
            diagnostics.get("analysis_graph_reduced", False)
        ),
        "structural_blocker_count": len(diagnostics.get("remaining_blockers", [])),
        "remaining_blockers": list(diagnostics.get("remaining_blockers", [])),
        "review_required": True,
        "acceptance_gate_closure_candidate_count": 0,
        "acceptance_ready": False,
        "publication_ready": False,
        "claim_boundary": (
            "This packet summarizes Morris sensitivity diagnostics for human "
            "review. It does not create data/manifests/sensitivity_acceptance.json, "
            "does not close the sensitivity gate, and does not claim calibrated "
            "real-world sensitivity results."
        ),
        "review_items": [
            "review unavailable or unexplained missing Morris indices before manuscript use",
            "interpret zero mu_star rows as diagnostic evidence, not calibrated no-effect proof",
            "resolve graph-scale scope before using reduced-graph sensitivity outputs in final claims",
            "decide whether Morris screening is sufficient or a Sobol extension is required",
            "record any gate decision only in a separate sensitivity acceptance record",
        ],
    }
    with manifest.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return value


def _structural_readiness_row(
    diagnostics: Mapping[str, Any],
    evidence_paths: str,
) -> dict[str, str]:
    ready = bool(diagnostics.get("diagnostics_ready", False))
    blockers = [str(item) for item in diagnostics.get("remaining_blockers", [])]
    if ready:
        detail = (
            f"summary_rows={diagnostics.get('row_count', 0)}; "
            f"manifest_summary_rows={diagnostics.get('manifest_summary_row_count', '')}; "
            "expected_rows="
            f"{diagnostics.get('expected_summary_row_count_from_manifest_dimensions', '')}"
        )
        status = "ready_for_review"
        action = (
            "Confirm the Morris summary and manifest correspond to the selected "
            "final-study sensitivity run before any acceptance decision."
        )
    else:
        detail = "blockers=" + "; ".join(blockers)
        status = "blocked_by_structural_diagnostics"
        action = (
            "Regenerate or repair Morris summary and manifest artifacts before "
            "continuing sensitivity review."
        )
    return _review_row(
        category_id="structural_readiness",
        issue_category="Morris artifact structural readiness",
        diagnostic_status=status,
        affected_row_count=str(len(blockers)),
        diagnostic_detail=detail,
        review_action=action,
        publication_use_status="review_support_only_not_sensitivity_acceptance",
        evidence_paths=evidence_paths,
    )


def _index_issue_row(
    diagnostics: Mapping[str, Any],
    evidence_paths: str,
) -> dict[str, str]:
    affected = int(diagnostics.get("rows_with_index_issues", 0))
    unavailable = int(diagnostics.get("unavailable_index_row_count", 0))
    issue_counts = diagnostics.get("index_issue_counts", {})
    if not isinstance(issue_counts, Mapping):
        issue_counts = {}
    unavailable_counts = diagnostics.get("unavailable_index_status_counts", {})
    if not isinstance(unavailable_counts, Mapping):
        unavailable_counts = {}
    detail = "; ".join(
        f"{column}={int(issue_counts.get(column, 0))}"
        for column in MORRIS_INDEX_COLUMNS
    )
    if unavailable_counts:
        status_detail = ", ".join(
            f"{key}={int(value)}" for key, value in sorted(unavailable_counts.items())
        )
        detail = f"{detail}; unavailable_index_rows={unavailable}; {status_detail}"
    if affected:
        status = "review_required_missing_or_nonfinite_indices"
        action = (
            "Inspect affected metric-policy-scenario-parameter rows and document "
            "whether they are excluded, recalculated, or retained as unavailable "
            "index evidence."
        )
        publication_use_status = "blocked_from_final_claims_until_index_handling_review"
        row_count = affected
    elif unavailable:
        status = "review_required_unavailable_indices"
        action = (
            "Review the metric-policy-scenario groups with explicitly unavailable "
            "Morris indices and document how non-finite metric outputs are handled "
            "before manuscript use."
        )
        publication_use_status = "review_required_for_unavailable_indices_before_final_claims"
        row_count = unavailable
    else:
        status = "no_missing_or_nonfinite_indices_detected"
        action = (
            "Confirm index handling is complete before using sensitivity rankings."
        )
        publication_use_status = "review_required_before_final_sensitivity_claims"
        row_count = 0
    return _review_row(
        category_id="missing_or_nonfinite_morris_indices",
        issue_category="Morris index availability and non-finite values",
        diagnostic_status=status,
        affected_row_count=str(row_count),
        diagnostic_detail=detail,
        review_action=action,
        publication_use_status=publication_use_status,
        evidence_paths=evidence_paths,
    )


def _zero_mu_star_row(
    diagnostics: Mapping[str, Any],
    evidence_paths: str,
) -> dict[str, str]:
    affected = int(diagnostics.get("zero_mu_star_count", 0))
    status = (
        "review_required_zero_effect_rows"
        if affected
        else "no_zero_mu_star_rows_detected"
    )
    return _review_row(
        category_id="zero_mu_star_rows",
        issue_category="Zero mu_star rows",
        diagnostic_status=status,
        affected_row_count=str(affected),
        diagnostic_detail=(
            "zero_mu_star_count="
            f"{affected}; these may indicate inactive parameters, no output "
            "variation, censoring behavior, or insufficient sample separation"
        ),
        review_action=(
            "Review zero-effect rows before describing drivers of sensitivity; "
            "do not treat zeros as calibrated no-effect findings without a "
            "documented interpretation."
        ),
        publication_use_status="review_required_before_interpreting_parameter_rankings",
        evidence_paths=evidence_paths,
    )


def _reduced_graph_scope_row(
    diagnostics: Mapping[str, Any],
    morris_manifest: Mapping[str, Any],
    evidence_paths: str,
) -> dict[str, str]:
    reduced = bool(diagnostics.get("analysis_graph_reduced", False))
    affected = int(diagnostics.get("row_count", 0)) if reduced else 0
    status = (
        "review_required_reduced_analysis_graph"
        if reduced
        else "not_reduced_but_graph_scope_still_requires_review"
    )
    return _review_row(
        category_id="reduced_graph_scope",
        issue_category="Reduced analysis graph scope",
        diagnostic_status=status,
        affected_row_count=str(affected),
        diagnostic_detail=_graph_scope_detail(morris_manifest, reduced=reduced),
        review_action=(
            "Close the graph-scale method review or regenerate sensitivity "
            "outputs on the selected final graph method before final-study "
            "sensitivity claims."
        ),
        publication_use_status="blocked_until_graph_scale_and_sensitivity_acceptance",
        evidence_paths=evidence_paths,
    )


def _result_scope_row(
    diagnostics: Mapping[str, Any],
    evidence_paths: str,
) -> dict[str, str]:
    scope = str(diagnostics.get("result_scope", "")).strip()
    lowered = scope.lower()
    scaffold_scope = "scaffold" in lowered or "not calibrated" in lowered
    status = (
        "blocked_by_scaffold_or_not_calibrated_scope"
        if scaffold_scope
        else "result_scope_requires_human_review"
    )
    return _review_row(
        category_id="result_scope",
        issue_category="Sensitivity result claim scope",
        diagnostic_status=status,
        affected_row_count=str(int(diagnostics.get("row_count", 0))),
        diagnostic_detail=scope,
        review_action=(
            "Keep manuscript, report, and tables inside the scaffold "
            "decision-support boundary until a separate sensitivity acceptance "
            "record exists."
        ),
        publication_use_status="not_publication_ready_without_acceptance_record",
        evidence_paths=evidence_paths,
    )


def _sobol_decision_row(
    diagnostics: Mapping[str, Any],
    morris_manifest: Mapping[str, Any],
    evidence_paths: str,
) -> dict[str, str]:
    method = str(morris_manifest.get("method", "salib_morris") or "salib_morris")
    return _review_row(
        category_id="sobol_decision_requirement",
        issue_category="Sobol extension decision requirement",
        diagnostic_status="review_required_method_scope_decision",
        affected_row_count=str(int(diagnostics.get("row_count", 0))),
        diagnostic_detail=(
            f"current_method={method}; current packet summarizes Morris "
            "diagnostics only and does not run or waive Sobol analysis"
        ),
        review_action=(
            "Reviewer must decide whether Morris screening is sufficient for "
            "the final claim boundary or whether Sobol analysis is required; "
            "record that decision only in sensitivity_acceptance.json."
        ),
        publication_use_status="blocked_until_morris_vs_sobol_decision_is_recorded",
        evidence_paths=evidence_paths,
    )


def _review_row(
    *,
    category_id: str,
    issue_category: str,
    diagnostic_status: str,
    affected_row_count: str,
    diagnostic_detail: str,
    review_action: str,
    publication_use_status: str,
    evidence_paths: str,
) -> dict[str, str]:
    return {
        "category_id": category_id,
        "issue_category": issue_category,
        "diagnostic_status": diagnostic_status,
        "affected_row_count": affected_row_count,
        "diagnostic_detail": diagnostic_detail,
        "review_required": "true",
        "acceptance_ready": "false",
        "publication_ready": "false",
        "review_action": review_action,
        "publication_use_status": publication_use_status,
        "evidence_input_paths": evidence_paths,
        "claim_boundary": SENSITIVITY_REVIEW_PACKET_SCOPE,
    }


def _graph_scope_detail(
    manifest: Mapping[str, Any],
    *,
    reduced: bool,
) -> str:
    graph_scale = manifest.get("graph_scale", {})
    if not isinstance(graph_scale, Mapping):
        graph_scale = {}
    source = graph_scale.get("source", {})
    analysis = graph_scale.get("analysis", {})
    if not isinstance(source, Mapping):
        source = {}
    if not isinstance(analysis, Mapping):
        analysis = {}
    strategy = str(
        analysis.get("strategy", manifest.get("analysis_graph_strategy", ""))
    ).strip()
    return (
        f"source_nodes={source.get('nodes', manifest.get('source_graph_nodes', ''))}; "
        f"source_edges={source.get('edges', manifest.get('source_graph_edges', ''))}; "
        f"analysis_nodes={analysis.get('nodes', manifest.get('graph_nodes', ''))}; "
        f"analysis_edges={analysis.get('edges', manifest.get('graph_edges', ''))}; "
        f"analysis_graph_reduced={str(reduced).lower()}; "
        f"strategy={strategy}"
    )


def _load_json_object(path: str | Path) -> dict[str, Any]:
    json_path = Path(path)
    if not json_path.exists():
        return {}
    with json_path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    return value if isinstance(value, dict) else {}


def _evidence_path_text(
    summary_path: str | Path,
    morris_manifest_path: str | Path,
) -> str:
    return (
        f"morris_summary={_display_path(summary_path)}; "
        f"morris_manifest={_display_path(morris_manifest_path)}"
    )


def _display_path(path: str | Path) -> str:
    filepath = Path(path)
    try:
        return filepath.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return filepath.as_posix()


__all__ = [
    "DEFAULT_SENSITIVITY_REVIEW_MANIFEST_PATH",
    "DEFAULT_SENSITIVITY_REVIEW_PACKET_PATH",
    "SENSITIVITY_REVIEW_COLUMNS",
    "SENSITIVITY_REVIEW_PACKET_SCOPE",
    "build_sensitivity_review_rows",
    "write_sensitivity_review_packet",
]
