"""Graph-scale strategy review packet generation.

The graph-scale review packet lists the feasible source-vs-analysis graph
options. This module turns those options into explicit pre-review states
without accepting a graph-scale method or treating reduced-corridor outputs as
release-scope real-world evidence.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from src.realworld.graph_scale_review import (
    DEFAULT_GRAPH_SCALE_REVIEW_PACKET_PATH,
)
from src.realworld.full_graph_runtime_readiness_packet import (
    DEFAULT_FULL_GRAPH_RUNTIME_READINESS_MANIFEST_PATH,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_GRAPH_SCALE_STRATEGY_READINESS_PACKET_PATH = (
    PROJECT_ROOT / "data" / "validation" / "graph_scale_strategy_readiness_packet.csv"
)
DEFAULT_GRAPH_SCALE_STRATEGY_READINESS_MANIFEST_PATH = (
    PROJECT_ROOT
    / "data"
    / "validation"
    / "graph_scale_strategy_readiness_manifest.json"
)
DEFAULT_GRAPH_SCALE_STRATEGY_READINESS_DOC_PATH = (
    PROJECT_ROOT / "docs" / "graph_scale_strategy_readiness_packet.md"
)
DEFAULT_GRAPH_SCALE_RESULT_COMPARISON_MANIFEST_PATH = (
    PROJECT_ROOT
    / "data"
    / "validation"
    / "graph_scale_result_comparison_manifest.json"
)
DEFAULT_GRAPH_SCALE_ACCEPTANCE_PATH = (
    PROJECT_ROOT / "data" / "manifests" / "graph_scale_acceptance.json"
)
GRAPH_SCALE_STRATEGY_READINESS_SCOPE = (
    "Graph-scale strategy review packet only; not graph-scale acceptance, "
    "not calibrated real-world validation, not traffic model validation, not "
    "operational routing evidence, and not publication approval."
)
GRAPH_SCALE_STRATEGY_READINESS_COLUMNS: tuple[str, ...] = (
    "option_id",
    "option_label",
    "region_id",
    "source_graph_nodes",
    "source_graph_edges",
    "analysis_graph_nodes",
    "analysis_graph_edges",
    "analysis_graph_reduced",
    "experiment_run_profile",
    "experiment_row_count",
    "experiment_summary_row_count",
    "readiness_status",
    "blocking_reason",
    "required_reviewer_action",
    "available_evidence",
    "result_comparison_signal",
    "publication_use_status",
    "can_support_graph_scale_gate",
    "claim_boundary",
)


def build_graph_scale_strategy_readiness_rows(
    *,
    review_rows: Sequence[Mapping[str, str]] | None = None,
    review_packet_path: str | Path = DEFAULT_GRAPH_SCALE_REVIEW_PACKET_PATH,
    result_comparison_manifest_path: str
    | Path = DEFAULT_GRAPH_SCALE_RESULT_COMPARISON_MANIFEST_PATH,
    acceptance_path: str | Path = DEFAULT_GRAPH_SCALE_ACCEPTANCE_PATH,
) -> list[dict[str, str]]:
    """Return graph-scale strategy review rows for current method options."""

    rows = (
        list(review_rows)
        if review_rows is not None
        else _load_review_rows(review_packet_path)
    )
    result_manifest = _load_json_object(result_comparison_manifest_path)
    full_multi_corridor_profile_available = _full_multi_corridor_profile_available(rows)
    readiness_rows = [
        _readiness_row(
            row,
            result_manifest=result_manifest,
            full_multi_corridor_profile_available=full_multi_corridor_profile_available,
        )
        for row in rows
    ]
    acceptance = Path(acceptance_path)
    readiness_rows.append(_acceptance_requirement_row(acceptance))
    return readiness_rows


def write_graph_scale_strategy_readiness_packet(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_GRAPH_SCALE_STRATEGY_READINESS_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_GRAPH_SCALE_STRATEGY_READINESS_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_GRAPH_SCALE_STRATEGY_READINESS_DOC_PATH,
    review_packet_path: str | Path = DEFAULT_GRAPH_SCALE_REVIEW_PACKET_PATH,
    result_comparison_manifest_path: str
    | Path = DEFAULT_GRAPH_SCALE_RESULT_COMPARISON_MANIFEST_PATH,
    full_graph_runtime_readiness_manifest_path: str
    | Path = DEFAULT_FULL_GRAPH_RUNTIME_READINESS_MANIFEST_PATH,
) -> dict[str, Any]:
    """Write graph-scale strategy review CSV, manifest, and Markdown."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=GRAPH_SCALE_STRATEGY_READINESS_COLUMNS,
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    column: str(row.get(column, ""))
                    for column in GRAPH_SCALE_STRATEGY_READINESS_COLUMNS
                }
            )

    summary = build_graph_scale_strategy_readiness_manifest(
        rows=rows,
        output_path=output,
        manifest_path=manifest,
        doc_path=doc,
        review_packet_path=review_packet_path,
        result_comparison_manifest_path=result_comparison_manifest_path,
        full_graph_runtime_readiness_manifest_path=(
            full_graph_runtime_readiness_manifest_path
        ),
    )
    manifest.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    doc.write_text(
        build_graph_scale_strategy_readiness_markdown(summary, rows=rows),
        encoding="utf-8",
    )
    return summary


def build_graph_scale_strategy_readiness_manifest(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_GRAPH_SCALE_STRATEGY_READINESS_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_GRAPH_SCALE_STRATEGY_READINESS_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_GRAPH_SCALE_STRATEGY_READINESS_DOC_PATH,
    review_packet_path: str | Path = DEFAULT_GRAPH_SCALE_REVIEW_PACKET_PATH,
    result_comparison_manifest_path: str
    | Path = DEFAULT_GRAPH_SCALE_RESULT_COMPARISON_MANIFEST_PATH,
    full_graph_runtime_readiness_manifest_path: str
    | Path = DEFAULT_FULL_GRAPH_RUNTIME_READINESS_MANIFEST_PATH,
) -> dict[str, Any]:
    """Return a conservative manifest for graph-scale strategy review."""

    status_counts = _counts(row.get("readiness_status", "") for row in rows)
    runtime_manifest = _load_json_object(full_graph_runtime_readiness_manifest_path)
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
            GRAPH_SCALE_STRATEGY_READINESS_SCOPE
            + " This packet cannot close data/manifests/graph_scale_acceptance.json."
        ),
        "result_scope": GRAPH_SCALE_STRATEGY_READINESS_SCOPE,
        "row_count": len(rows),
        "readiness_status_counts": status_counts,
        "blocking_request_count": blocking_count,
        "human_review_request_count": human_review_count,
        "graph_scale_gate_closure_candidate_count": 0,
        "publication_ready": False,
        "can_mark_complete": False,
        "inputs": {
            "graph_scale_review_packet": _display_path(Path(review_packet_path)),
            "graph_scale_result_comparison_manifest": _display_path(
                Path(result_comparison_manifest_path)
            ),
            "full_graph_runtime_readiness_manifest": _display_path(
                Path(full_graph_runtime_readiness_manifest_path)
            ),
        },
        "outputs": {
            "csv": _display_path(Path(output_path)),
            "manifest": _display_path(Path(manifest_path)),
            "doc": _display_path(Path(doc_path)),
        },
        "review_items": [
            "decide whether the 118-node reduced corridor is acceptable or only a smoke shortcut",
            "decide whether the 164-node full-profile multi-corridor candidate should replace the current analysis graph",
            "review graph-sensitive result differences before interpreting policy outcomes",
            "review the full-graph runtime packet before selecting or excluding full-graph execution",
            "generate full-graph outputs or record why full-graph execution is outside the selected scope",
            "record the release-scope graph-scale method only in data/manifests/graph_scale_acceptance.json",
        ],
        "full_graph_runtime_readiness": _runtime_manifest_summary(runtime_manifest),
        "remaining_blockers": _remaining_blockers(
            rows,
            extra=[
                "current reduced-corridor output has alternate-route warnings",
                "full bus-practical graph has smoke/runtime evidence only, not full scenario-policy-seed output",
                "selected graph choice still requires downstream regeneration decisions for sensitivity, figures, tables, and manuscript interpretation",
            ],
        ),
    }


def build_graph_scale_strategy_readiness_markdown(
    manifest: Mapping[str, Any],
    *,
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Return a human-readable graph-scale strategy review packet."""

    lines = [
        "# Graph-Scale Strategy Review Packet",
        "",
        str(manifest.get("claim_boundary", GRAPH_SCALE_STRATEGY_READINESS_SCOPE)),
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
        "## Full-Graph Runtime Review",
        "",
        f"- Manifest present: `{str((manifest.get('full_graph_runtime_readiness') or {}).get('manifest_present', False)).lower()}`",
        f"- Blocking requests: {(manifest.get('full_graph_runtime_readiness') or {}).get('blocking_request_count', 0)}",
        f"- Human-review requests: {(manifest.get('full_graph_runtime_readiness') or {}).get('human_review_request_count', 0)}",
        f"- Can mark complete: `{str((manifest.get('full_graph_runtime_readiness') or {}).get('can_mark_complete', False)).lower()}`",
        "",
        "## Strategy Review Rows",
        "",
        "| Option | Status | Evidence | Required Action |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {option} | {status} | {evidence} | {action} |".format(
                option=_cell(row.get("option_id", "")),
                status=_cell(row.get("readiness_status", "")),
                evidence=_cell(row.get("available_evidence", "")),
                action=_cell(row.get("required_reviewer_action", "")),
            )
        )
    lines.extend(
        [
            "",
            "## Required Reviewer Actions",
            "",
            "- Choose the selected graph-scale method only after reviewing route preservation, result deltas, runtime scope, and downstream regeneration impact.",
            "- Keep reduced-corridor and multi-corridor outputs in scaffold scope until the selected method has a formal graph-scale decision record.",
            "- Do not treat this packet as graph-scale acceptance or calibrated network validation.",
            "",
        ]
    )
    return "\n".join(lines)


def _readiness_row(
    row: Mapping[str, str],
    *,
    result_manifest: Mapping[str, Any],
    full_multi_corridor_profile_available: bool,
) -> dict[str, str]:
    status, reason, action = _classify_option(
        row,
        result_manifest=result_manifest,
        full_multi_corridor_profile_available=full_multi_corridor_profile_available,
    )
    return {
        "option_id": str(row.get("option_id", "")),
        "option_label": str(row.get("option_label", "")),
        "region_id": str(row.get("region_id", "")),
        "source_graph_nodes": str(row.get("source_graph_nodes", "")),
        "source_graph_edges": str(row.get("source_graph_edges", "")),
        "analysis_graph_nodes": str(row.get("analysis_graph_nodes", "")),
        "analysis_graph_edges": str(row.get("analysis_graph_edges", "")),
        "analysis_graph_reduced": str(row.get("analysis_graph_reduced", "")),
        "experiment_run_profile": str(row.get("experiment_run_profile", "")),
        "experiment_row_count": str(row.get("experiment_row_count", "")),
        "experiment_summary_row_count": str(row.get("experiment_summary_row_count", "")),
        "readiness_status": status,
        "blocking_reason": reason,
        "required_reviewer_action": action,
        "available_evidence": str(row.get("available_evidence", "")),
        "result_comparison_signal": _result_comparison_signal(result_manifest),
        "publication_use_status": str(row.get("publication_use_status", "")),
        "can_support_graph_scale_gate": "false",
        "claim_boundary": GRAPH_SCALE_STRATEGY_READINESS_SCOPE,
    }


def _acceptance_requirement_row(acceptance_path: Path) -> dict[str, str]:
    return {
        "option_id": "graph_scale_acceptance_record",
        "option_label": "Formal graph-scale acceptance record",
        "region_id": "",
        "source_graph_nodes": "",
        "source_graph_edges": "",
        "analysis_graph_nodes": "",
        "analysis_graph_edges": "",
        "analysis_graph_reduced": "",
        "experiment_run_profile": "",
        "experiment_row_count": "",
        "experiment_summary_row_count": "",
        "readiness_status": (
            "needs_human_review_graph_scale_acceptance_record"
            if acceptance_path.exists()
            else "blocked_missing_graph_scale_acceptance_record"
        ),
        "blocking_reason": (
            ""
            if acceptance_path.exists()
            else "data/manifests/graph_scale_acceptance.json is absent"
        ),
        "required_reviewer_action": (
            "review the existing graph-scale decision record"
            if acceptance_path.exists()
            else "record the selected graph-scale method only after source-vs-analysis graph review"
        ),
        "available_evidence": _display_path(acceptance_path),
        "result_comparison_signal": "",
        "publication_use_status": "blocked_until_graph_scale_decision",
        "can_support_graph_scale_gate": "false",
        "claim_boundary": GRAPH_SCALE_STRATEGY_READINESS_SCOPE,
    }


def _remaining_blockers(
    rows: Sequence[Mapping[str, str]],
    *,
    extra: Sequence[str] = (),
) -> list[str]:
    blockers: list[str] = []
    for row in rows:
        status = str(row.get("readiness_status", ""))
        reason = str(row.get("blocking_reason", "")).strip()
        if status.startswith("blocked_") and reason:
            blockers.append(reason)
    blockers.extend(str(reason).strip() for reason in extra if str(reason).strip())
    return list(dict.fromkeys(blockers))


def _classify_option(
    row: Mapping[str, str],
    *,
    result_manifest: Mapping[str, Any],
    full_multi_corridor_profile_available: bool,
) -> tuple[str, str, str]:
    option_id = str(row.get("option_id", ""))
    alternate_warn = _int(row.get("alternate_route_warn"))
    alternate_paths_preserved = _true(row.get("alternate_paths_preserved"))
    experiment_rows = _int(row.get("experiment_row_count"))

    if option_id == "current_reduced_corridor":
        if alternate_warn > 0 or not alternate_paths_preserved:
            return (
                "needs_human_review_reduced_corridor_alternate_route_warnings",
                "",
                "review whether omitted alternate paths are acceptable or require multi-corridor/full-graph execution",
            )
        return (
            "needs_human_review_reduced_corridor_scope",
            "",
            "review whether the reduced corridor is acceptable for release-scope claims",
        )
    if option_id == "multi_corridor_candidate":
        if experiment_rows < 1000:
            if full_multi_corridor_profile_available:
                return (
                    "needs_human_review_multi_corridor_sample_scope",
                    "",
                    "treat the separated candidate as route-preservation/smoke evidence and review the full-profile candidate before method selection",
                )
            return (
                "blocked_incomplete_multi_corridor_run_profile",
                "multi-corridor candidate has only separated/sample-scale output",
                "use the full-profile candidate or regenerate the selected experiment package on this graph",
            )
        return (
            "needs_human_review_multi_corridor_candidate_scope",
            "",
            "review candidate output scope and downstream regeneration requirements",
        )
    if option_id == "multi_corridor_full_candidate":
        if _result_manifest_has_nontrivial_deltas(result_manifest):
            return (
                "needs_human_review_multi_corridor_result_deltas",
                "",
                "review candidate_worsens and nonfinite result differences before selecting this graph method",
            )
        return (
            "needs_human_review_multi_corridor_full_candidate",
            "",
            "review the full-profile multi-corridor candidate as the potential selected method",
        )
    if option_id == "full_bus_practical_graph":
        if experiment_rows <= 0:
            return (
                "blocked_missing_full_graph_experiment_outputs",
                "full bus-practical graph has smoke evidence only",
                "generate full-graph outputs or explicitly bound release-scope claims away from full-graph execution",
            )
        return (
            "needs_human_review_full_graph_outputs",
            "",
            "review full-graph outputs and runtime scope before graph-scale decision",
        )
    return (
        "blocked_unclassified_graph_scale_option",
        f"unrecognized option_id {option_id!r}",
        "classify this graph-scale option before strategy review",
    )


def _result_manifest_has_nontrivial_deltas(manifest: Mapping[str, Any]) -> bool:
    counts = manifest.get("comparison_status_counts", {})
    if not isinstance(counts, Mapping):
        return False
    return _int(counts.get("candidate_worsens")) > 0 or _int(
        counts.get("nonfinite_difference")
    ) > 0


def _full_multi_corridor_profile_available(rows: Sequence[Mapping[str, str]]) -> bool:
    for row in rows:
        if str(row.get("option_id", "")) != "multi_corridor_full_candidate":
            continue
        return _int(row.get("experiment_row_count")) >= 1000
    return False


def _result_comparison_signal(manifest: Mapping[str, Any]) -> str:
    counts = manifest.get("comparison_status_counts", {})
    if not isinstance(counts, Mapping):
        return "result_comparison_manifest_missing_or_invalid"
    parts = [
        f"{key}={counts.get(key, 0)}"
        for key in (
            "candidate_improves",
            "candidate_worsens",
            "nonfinite_difference",
            "same_or_close",
        )
    ]
    return "; ".join(parts)


def _load_review_rows(path: str | Path) -> list[dict[str, str]]:
    packet = Path(path)
    if not packet.exists():
        return []
    with packet.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _load_json_object(path: str | Path) -> dict[str, Any]:
    json_path = Path(path)
    if not json_path.exists():
        return {}
    with json_path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    return value if isinstance(value, dict) else {}


def _runtime_manifest_summary(manifest: Mapping[str, Any]) -> dict[str, Any]:
    if not manifest:
        return {
            "manifest_present": False,
            "blocking_request_count": 0,
            "human_review_request_count": 0,
            "can_mark_complete": False,
        }
    return {
        "manifest_present": True,
        "row_count": _int(manifest.get("row_count")),
        "blocking_request_count": _int(manifest.get("blocking_request_count")),
        "human_review_request_count": _int(
            manifest.get("human_review_request_count")
        ),
        "readiness_status_counts": manifest.get("readiness_status_counts", {}),
        "can_mark_complete": bool(manifest.get("can_mark_complete", False)),
    }


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


def _true(value: object) -> bool:
    return str(value).strip().lower() == "true"


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", "<br>")


__all__ = [
    "DEFAULT_FULL_GRAPH_RUNTIME_READINESS_MANIFEST_PATH",
    "DEFAULT_GRAPH_SCALE_ACCEPTANCE_PATH",
    "DEFAULT_GRAPH_SCALE_RESULT_COMPARISON_MANIFEST_PATH",
    "DEFAULT_GRAPH_SCALE_STRATEGY_READINESS_DOC_PATH",
    "DEFAULT_GRAPH_SCALE_STRATEGY_READINESS_MANIFEST_PATH",
    "DEFAULT_GRAPH_SCALE_STRATEGY_READINESS_PACKET_PATH",
    "GRAPH_SCALE_STRATEGY_READINESS_COLUMNS",
    "GRAPH_SCALE_STRATEGY_READINESS_SCOPE",
    "build_graph_scale_strategy_readiness_manifest",
    "build_graph_scale_strategy_readiness_markdown",
    "build_graph_scale_strategy_readiness_rows",
    "write_graph_scale_strategy_readiness_packet",
]
