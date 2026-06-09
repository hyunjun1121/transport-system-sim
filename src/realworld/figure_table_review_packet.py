"""Focused figure/table readiness worksheet for manuscript review.

The figure/table manifest already labels current outputs as scaffold-only.
This module turns that status into explicit reviewer rows for artifact
inventory, table lineage, caption boundaries, graph scope, sensitivity-index
handling, proxy-result interpretation, upstream evidence dependencies, and
formal manuscript decision. It does not create
``data/manifests/manuscript_acceptance.json`` or approve any figure/table.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from src.realworld.manuscript_acceptance import DEFAULT_MANUSCRIPT_ACCEPTANCE_PATH


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FIGURE_TABLE_MANIFEST_PATH = (
    PROJECT_ROOT
    / "results"
    / "realworld_pilot"
    / "tables"
    / "figure_table_manifest.json"
)
DEFAULT_FIGURE_TABLE_REVIEW_PACKET_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "figure_table_review_packet.csv"
)
DEFAULT_FIGURE_TABLE_REVIEW_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "figure_table_review_manifest.json"
)
DEFAULT_FIGURE_TABLE_REVIEW_DOC_PATH = (
    PROJECT_ROOT / "docs" / "figure_table_review_packet.md"
)
FIGURE_TABLE_REVIEW_SCOPE = (
    "Figure/table review packet only; not manuscript decision, not "
    "calibrated real-world results, and not operational routing evidence."
)
FIGURE_TABLE_REVIEW_COLUMNS: tuple[str, ...] = (
    "review_id",
    "review_topic",
    "current_evidence",
    "review_status",
    "blocking_reason",
    "required_reviewer_action",
    "followup_artifacts",
    "evidence_input_paths",
    "can_support_manuscript_gate",
    "claim_boundary",
)


def build_figure_table_review_rows(
    *,
    figure_manifest_path: str | Path = DEFAULT_FIGURE_TABLE_MANIFEST_PATH,
    manuscript_acceptance_path: str | Path = DEFAULT_MANUSCRIPT_ACCEPTANCE_PATH,
) -> list[dict[str, str]]:
    """Return reviewer rows for the current figure/table package."""

    manifest_path = Path(figure_manifest_path)
    acceptance_path = Path(manuscript_acceptance_path)
    manifest = _read_json_object(manifest_path)
    figures = _dict_value(manifest, "figures")
    tables = _dict_value(manifest, "tables")
    row_counts = _dict_value(manifest, "row_counts")
    graph_scale = _dict_value(manifest, "graph_scale")
    morris_handling = _dict_value(manifest, "morris_index_handling")
    result_scope = str(manifest.get("result_scope", ""))
    claim_boundary = str(manifest.get("claim_boundary", ""))
    evidence_paths = _evidence_paths(manifest_path=manifest_path, manifest=manifest)
    missing_paths = _missing_artifact_paths(figures=figures, tables=tables)
    row_count_mismatches = _row_count_mismatches(
        row_counts=row_counts,
        tables=tables,
    )
    captions_missing_boundary = _captions_missing_boundary(figures)
    graph_reduced = _graph_scope_is_reduced(graph_scale)
    source_scaffold = _source_scopes_are_scaffold(manifest)
    morris_visible = all(
        key in morris_handling
        for key in ("audit", "figures", "tables")
    )

    return [
        _row(
            review_id="artifact_inventory",
            review_topic="Figure and table artifact inventory",
            current_evidence=(
                f"figures={len(figures)}; tables={len(tables)}; "
                f"missing_paths={len(missing_paths)}"
            ),
            review_status=(
                "blocked_missing_figure_or_table_artifact"
                if missing_paths
                else "needs_human_review_artifact_inventory"
            ),
            blocking_reason=(
                "; ".join(missing_paths)
                if missing_paths
                else ""
            ),
            required_reviewer_action=(
                "Confirm every listed figure/table exists and is regenerated "
                "from the current pilot and sensitivity outputs."
            ),
            followup_artifacts=(
                "results/realworld_pilot/tables/figure_table_manifest.json; "
                "data/manifests/manuscript_acceptance.json"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            review_id="table_lineage_and_row_counts",
            review_topic="Table lineage and row-count checks",
            current_evidence=(
                f"manifest_row_counts={_join_counts(row_counts)}; "
                f"row_count_mismatches={len(row_count_mismatches)}"
            ),
            review_status=(
                "blocked_table_row_count_mismatch"
                if row_count_mismatches
                else "needs_human_review_table_lineage"
            ),
            blocking_reason=(
                "; ".join(row_count_mismatches)
                if row_count_mismatches
                else ""
            ),
            required_reviewer_action=(
                "Verify tables were regenerated from current CSV outputs and "
                "that row counts match the manifest before manuscript review."
            ),
            followup_artifacts=(
                "results/realworld_pilot/tables/main_result_table.csv; "
                "results/realworld_pilot/tables/sensitivity_result_table.csv; "
                "results/realworld_pilot/tables/claim_boundary_table.csv"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            review_id="caption_and_claim_boundary",
            review_topic="Figure captions and claim-boundary language",
            current_evidence=(
                f"result_scope={result_scope}; claim_boundary={claim_boundary}; "
                f"captions_missing_boundary={len(captions_missing_boundary)}"
            ),
            review_status=(
                "blocked_missing_caption_claim_boundary"
                if captions_missing_boundary
                else "needs_human_review_caption_boundary"
            ),
            blocking_reason=(
                "; ".join(captions_missing_boundary)
                if captions_missing_boundary
                else ""
            ),
            required_reviewer_action=(
                "Keep captions and table language explicit that current figures "
                "are scaffold-only until final evidence gates and manuscript "
                "acceptance close."
            ),
            followup_artifacts=(
                "docs/claim_alignment_review_packet.md; "
                "data/manifests/manuscript_acceptance.json"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            review_id="graph_scope_dependency",
            review_topic="Graph-scope dependency",
            current_evidence=_graph_evidence(graph_scale),
            review_status=(
                "blocked_reduced_graph_scope_dependency"
                if graph_reduced
                else "needs_human_review_graph_scope_dependency"
            ),
            blocking_reason=(
                "figure/table outputs depend on reduced analysis graph scope"
                if graph_reduced
                else ""
            ),
            required_reviewer_action=(
                "Review graph-scale acceptance before using figures/tables as "
                "publication-result evidence."
            ),
            followup_artifacts=(
                "data/manifests/graph_scale_acceptance.json; "
                "results/realworld_pilot/tables/figure_table_manifest.json"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            review_id="sensitivity_index_handling",
            review_topic="Sensitivity-index handling in tables and ranking figure",
            current_evidence=(
                f"morris_index_handling_fields={','.join(sorted(morris_handling))}; "
                f"selected_metric={manifest.get('selected_sensitivity_metric', '')}"
            ),
            review_status=(
                "needs_human_review_morris_index_handling"
                if morris_visible
                else "blocked_missing_morris_index_handling"
            ),
            blocking_reason=(
                ""
                if morris_visible
                else "figure/table manifest lacks Morris index handling notes"
            ),
            required_reviewer_action=(
                "Review how blank, masked, NaN, or non-finite Morris rows are "
                "kept in tables and excluded from plotted top rankings."
            ),
            followup_artifacts=(
                "data/validation/sensitivity_index_review_packet.csv; "
                "data/manifests/sensitivity_acceptance.json"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            review_id="bottleneck_and_regime_interpretation",
            review_topic="Bottleneck and policy-regime interpretation",
            current_evidence=(
                f"bottleneck_rows={row_counts.get('bottleneck_attribution_table', '')}; "
                f"policy_regime_rows={row_counts.get('policy_regime_table', '')}"
            ),
            review_status="needs_human_review_proxy_interpretation",
            blocking_reason="",
            required_reviewer_action=(
                "Treat bottleneck attribution and policy-regime rows as proxy "
                "interpretation aids, not causal bottleneck evidence, until "
                "benchmark-reviewed and decision-reviewed."
            ),
            followup_artifacts=(
                "results/realworld_pilot/tables/bottleneck_attribution_table.csv; "
                "results/realworld_pilot/tables/policy_regime_table.csv"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            review_id="upstream_evidence_dependency",
            review_topic="Upstream evidence and result-scope dependency",
            current_evidence=(
                f"source_scopes_scaffold={str(source_scaffold).lower()}; "
                f"result_scope={result_scope}"
            ),
            review_status=(
                "blocked_upstream_evidence_dependency"
                if source_scaffold
                else "needs_human_review_upstream_evidence_dependency"
            ),
            blocking_reason=(
                "figure/table source outputs remain scaffold or not calibrated"
                if source_scaffold
                else ""
            ),
            required_reviewer_action=(
                "Do not promote current figures/tables into release-scope manuscript "
                "claims until pilot inputs, validation, experiments, and "
                "sensitivity outputs are decision-reviewed or regenerated."
            ),
            followup_artifacts=(
                "data/manifests/experiment_acceptance.json; "
                "data/manifests/sensitivity_acceptance.json; "
                "data/manifests/manuscript_acceptance.json"
            ),
            evidence_input_paths=evidence_paths,
        ),
        _row(
            review_id="formal_manuscript_acceptance_boundary",
            review_topic="Formal manuscript decision boundary",
            current_evidence=(
                f"manuscript_acceptance_present={str(acceptance_path.exists()).lower()}"
            ),
            review_status=(
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
                "Record figure/table review only in formal manuscript "
                "acceptance after evidence gates and result claims are reviewed."
            ),
            followup_artifacts="data/manifests/manuscript_acceptance.json",
            evidence_input_paths=evidence_paths,
        ),
    ]


def write_figure_table_review_packet(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_FIGURE_TABLE_REVIEW_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_FIGURE_TABLE_REVIEW_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_FIGURE_TABLE_REVIEW_DOC_PATH,
    figure_manifest_path: str | Path = DEFAULT_FIGURE_TABLE_MANIFEST_PATH,
) -> dict[str, Any]:
    """Write CSV, JSON, and Markdown figure/table review artifacts."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIGURE_TABLE_REVIEW_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    column: str(row.get(column, ""))
                    for column in FIGURE_TABLE_REVIEW_COLUMNS
                }
            )

    summary = build_figure_table_review_manifest(
        rows=rows,
        output_path=output,
        manifest_path=manifest,
        doc_path=doc,
        figure_manifest_path=figure_manifest_path,
    )
    manifest.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    doc.write_text(
        build_figure_table_review_markdown(summary, rows=rows),
        encoding="utf-8",
    )
    return summary


def build_figure_table_review_manifest(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_FIGURE_TABLE_REVIEW_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_FIGURE_TABLE_REVIEW_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_FIGURE_TABLE_REVIEW_DOC_PATH,
    figure_manifest_path: str | Path = DEFAULT_FIGURE_TABLE_MANIFEST_PATH,
) -> dict[str, Any]:
    """Return a conservative summary for figure/table review rows."""

    statuses = _counts(row.get("review_status", "") for row in rows)
    blocking_count = sum(
        1 for row in rows if str(row.get("review_status", "")).startswith("blocked")
    )
    human_review_count = sum(
        1
        for row in rows
        if str(row.get("review_status", "")).startswith("needs_human_review")
    )
    return {
        "schema_version": 1,
        "claim_boundary": (
            FIGURE_TABLE_REVIEW_SCOPE
            + " It cannot create or replace data/manifests/manuscript_acceptance.json."
        ),
        "result_scope": FIGURE_TABLE_REVIEW_SCOPE,
        "row_count": len(rows),
        "review_status_counts": statuses,
        "blocking_review_count": blocking_count,
        "human_review_count": human_review_count,
        "manuscript_gate_closure_candidate_count": 0,
        "publication_ready": False,
        "can_mark_complete": False,
        "inputs": {
            "figure_table_manifest": _display_path(Path(figure_manifest_path)),
        },
        "outputs": {
            "csv": _display_path(Path(output_path)),
            "manifest": _display_path(Path(manifest_path)),
            "doc": _display_path(Path(doc_path)),
        },
        "review_items": [
            "verify figure/table artifacts exist and were regenerated from current outputs",
            "review caption and claim-boundary language before the manuscript decision",
            "resolve graph-scale, experiment, benchmark, and sensitivity decision dependencies before release-scope figure claims",
            "record reviewer-selected figure/table review only in data/manifests/manuscript_acceptance.json",
        ],
        "remaining_blockers": _remaining_blockers(rows),
    }


def build_figure_table_review_markdown(
    manifest: Mapping[str, Any],
    *,
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Return a human-readable figure/table review packet."""

    lines = [
        "# Figure/Table Review Packet",
        "",
        str(manifest.get("claim_boundary", FIGURE_TABLE_REVIEW_SCOPE)),
        "",
        "## Verdict",
        "",
        f"- Publication ready: `{str(manifest.get('publication_ready', False)).lower()}`",
        f"- Can mark complete: `{str(manifest.get('can_mark_complete', False)).lower()}`",
        f"- Review rows: {manifest.get('row_count', 0)}",
        f"- Blocking reviews: {manifest.get('blocking_review_count', 0)}",
        f"- Human-review rows: {manifest.get('human_review_count', 0)}",
        f"- Status counts: `{manifest.get('review_status_counts', {})}`",
        "",
        "## Review Rows",
        "",
        "| Review | Status | Evidence | Required Action |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {review} | {status} | {evidence} | {action} |".format(
                review=_cell(row.get("review_id", "")),
                status=_cell(row.get("review_status", "")),
                evidence=_cell(row.get("current_evidence", "")),
                action=_cell(row.get("required_reviewer_action", "")),
            )
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This packet does not approve figure/table use in release-scope manuscript claims.",
            "- It does not replace graph-scale, experiment, sensitivity, benchmark, or manuscript decision records.",
            "- Keep figures/tables in scaffold scope until the formal manuscript decision is reviewed.",
            "",
        ]
    )
    return "\n".join(lines)


def _row(
    *,
    review_id: str,
    review_topic: str,
    current_evidence: str,
    review_status: str,
    blocking_reason: str,
    required_reviewer_action: str,
    followup_artifacts: str,
    evidence_input_paths: str,
) -> dict[str, str]:
    return {
        "review_id": review_id,
        "review_topic": review_topic,
        "current_evidence": current_evidence,
        "review_status": review_status,
        "blocking_reason": blocking_reason,
        "required_reviewer_action": required_reviewer_action,
        "followup_artifacts": followup_artifacts,
        "evidence_input_paths": evidence_input_paths,
        "can_support_manuscript_gate": "false",
        "claim_boundary": FIGURE_TABLE_REVIEW_SCOPE,
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


def _dict_value(mapping: Mapping[str, Any], key: str) -> dict[str, Any]:
    value = mapping.get(key, {})
    if isinstance(value, dict):
        return dict(value)
    return {}


def _evidence_paths(
    *,
    manifest_path: Path,
    manifest: Mapping[str, Any],
) -> str:
    paths: list[str] = [_display_path(manifest_path)]
    for section in ("figures", "tables", "inputs"):
        value = manifest.get(section, {})
        if isinstance(value, Mapping):
            for item in value.values():
                if isinstance(item, Mapping):
                    path = item.get("path")
                else:
                    path = item
                if isinstance(path, str) and path:
                    paths.append(path)
    return "; ".join(dict.fromkeys(paths))


def _missing_artifact_paths(
    *,
    figures: Mapping[str, Any],
    tables: Mapping[str, Any],
) -> list[str]:
    missing: list[str] = []
    for value in list(figures.values()) + list(tables.values()):
        if isinstance(value, Mapping):
            path_value = value.get("path")
        else:
            path_value = value
        if not isinstance(path_value, str) or not path_value:
            continue
        path = PROJECT_ROOT / path_value
        if not path.exists():
            missing.append(path_value)
    return missing


def _row_count_mismatches(
    *,
    row_counts: Mapping[str, Any],
    tables: Mapping[str, Any],
) -> list[str]:
    mismatches: list[str] = []
    for table_id, expected in row_counts.items():
        path_value = tables.get(table_id)
        if not isinstance(path_value, str) or not path_value.endswith(".csv"):
            continue
        path = PROJECT_ROOT / path_value
        if not path.exists():
            continue
        actual = _csv_data_row_count(path)
        expected_int = _int(expected)
        if expected_int != actual:
            mismatches.append(f"{table_id}: expected {expected_int}, found {actual}")
    return mismatches


def _csv_data_row_count(path: Path) -> int:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        try:
            next(reader)
        except StopIteration:
            return 0
        return sum(1 for _ in reader)


def _captions_missing_boundary(figures: Mapping[str, Any]) -> list[str]:
    missing: list[str] = []
    for figure_id, value in figures.items():
        if not isinstance(value, Mapping):
            missing.append(str(figure_id))
            continue
        note = str(value.get("caption_note", "")).lower()
        if "not calibrated" not in note or "operational" not in note:
            missing.append(str(figure_id))
    return missing


def _graph_scope_is_reduced(graph_scale: Mapping[str, Any]) -> bool:
    for value in graph_scale.values():
        if not isinstance(value, Mapping):
            continue
        analysis = value.get("analysis", {})
        if isinstance(analysis, Mapping) and bool(analysis.get("reduced")):
            return True
    return False


def _source_scopes_are_scaffold(manifest: Mapping[str, Any]) -> bool:
    scopes = [str(manifest.get("result_scope", "")), str(manifest.get("claim_boundary", ""))]
    source_scopes = manifest.get("source_result_scopes", {})
    if isinstance(source_scopes, Mapping):
        scopes.extend(str(item) for item in source_scopes.values())
    text = " ".join(scopes).lower()
    return any(term in text for term in ("scaffold", "not calibrated", "operational forecast"))


def _graph_evidence(graph_scale: Mapping[str, Any]) -> str:
    parts: list[str] = []
    for name, value in graph_scale.items():
        if not isinstance(value, Mapping):
            continue
        source = value.get("source", {})
        analysis = value.get("analysis", {})
        if not isinstance(source, Mapping) or not isinstance(analysis, Mapping):
            continue
        parts.append(
            "{name}: source={source_nodes}/{source_edges}; analysis={analysis_nodes}/{analysis_edges}; reduced={reduced}".format(
                name=name,
                source_nodes=source.get("nodes", ""),
                source_edges=source.get("edges", ""),
                analysis_nodes=analysis.get("nodes", ""),
                analysis_edges=analysis.get("edges", ""),
                reduced=str(analysis.get("reduced", "")).lower(),
            )
        )
    return "; ".join(parts)


def _join_counts(row_counts: Mapping[str, Any]) -> str:
    return "; ".join(f"{key}={value}" for key, value in sorted(row_counts.items()))


def _counts(values: Iterable[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value)
        if not key:
            continue
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _remaining_blockers(rows: Sequence[Mapping[str, str]]) -> list[str]:
    blockers: list[str] = []
    for row in rows:
        status = str(row.get("review_status", ""))
        if not status.startswith("blocked"):
            continue
        reason = str(row.get("blocking_reason", "")).strip()
        if reason:
            blockers.append(reason)
        else:
            blockers.append(str(row.get("required_reviewer_action", "")).strip())
    return blockers


def _int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


__all__ = [
    "DEFAULT_FIGURE_TABLE_MANIFEST_PATH",
    "DEFAULT_FIGURE_TABLE_REVIEW_DOC_PATH",
    "DEFAULT_FIGURE_TABLE_REVIEW_MANIFEST_PATH",
    "DEFAULT_FIGURE_TABLE_REVIEW_PACKET_PATH",
    "FIGURE_TABLE_REVIEW_COLUMNS",
    "FIGURE_TABLE_REVIEW_SCOPE",
    "build_figure_table_review_manifest",
    "build_figure_table_review_markdown",
    "build_figure_table_review_rows",
    "write_figure_table_review_packet",
]
