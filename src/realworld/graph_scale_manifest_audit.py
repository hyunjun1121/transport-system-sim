"""Audit graph-scale fields across generated pilot manifests.

The current study scaffold writes source and analysis graph counts into pilot,
sensitivity, Morris, statistics, and figure/table manifests. This module turns
those scattered fields into one reviewer packet without accepting any graph
method or final-study claim.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_GRAPH_SCALE_MANIFEST_AUDIT_PATH = (
    PROJECT_ROOT / "data" / "validation" / "graph_scale_manifest_audit.csv"
)
DEFAULT_GRAPH_SCALE_MANIFEST_AUDIT_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "validation" / "graph_scale_manifest_audit_manifest.json"
)
DEFAULT_GRAPH_SCALE_MANIFEST_AUDIT_DOC_PATH = (
    PROJECT_ROOT / "docs" / "graph_scale_manifest_audit.md"
)
DEFAULT_AUDITED_GRAPH_SCALE_MANIFEST_PATHS: tuple[Path, ...] = (
    PROJECT_ROOT / "results" / "realworld_pilot" / "pilot_result_manifest.json",
    PROJECT_ROOT / "results" / "realworld_pilot" / "pilot_sample_manifest.json",
    PROJECT_ROOT / "results" / "realworld_pilot" / "pilot_staged_manifest.json",
    PROJECT_ROOT / "results" / "realworld_pilot" / "pilot_full_manifest.json",
    PROJECT_ROOT / "results" / "realworld_pilot" / "pilot_multi_corridor_manifest.json",
    PROJECT_ROOT
    / "results"
    / "realworld_pilot"
    / "pilot_multi_corridor_full_manifest.json",
    PROJECT_ROOT / "results" / "realworld_pilot" / "sensitivity_manifest.json",
    PROJECT_ROOT / "results" / "realworld_pilot" / "morris_manifest.json",
    PROJECT_ROOT
    / "results"
    / "realworld_pilot"
    / "tables"
    / "pilot_full_statistics_manifest.json",
    PROJECT_ROOT
    / "results"
    / "realworld_pilot"
    / "tables"
    / "pilot_multi_corridor_statistics_manifest.json",
    PROJECT_ROOT
    / "results"
    / "realworld_pilot"
    / "tables"
    / "pilot_multi_corridor_full_statistics_manifest.json",
    PROJECT_ROOT
    / "results"
    / "realworld_pilot"
    / "tables"
    / "figure_table_manifest.json",
)
GRAPH_SCALE_MANIFEST_AUDIT_SCOPE = (
    "graph_scale_manifest_audit_review_aid_only_not_graph_scale_acceptance"
)
GRAPH_SCALE_MANIFEST_AUDIT_COLUMNS: tuple[str, ...] = (
    "manifest_path",
    "component_id",
    "artifact_family",
    "manifest_present",
    "graph_scale_present",
    "source_graph_nodes",
    "source_graph_edges",
    "analysis_graph_nodes",
    "analysis_graph_edges",
    "analysis_graph_reduced",
    "analysis_graph_strategy",
    "graph_source",
    "command",
    "run_profile_or_method",
    "result_scope",
    "coverage_status",
    "required_reviewer_action",
    "claim_boundary",
)


def build_graph_scale_manifest_audit_rows(
    *,
    manifest_paths: Sequence[str | Path] = DEFAULT_AUDITED_GRAPH_SCALE_MANIFEST_PATHS,
) -> list[dict[str, str]]:
    """Return one audit row per graph-scale component in each manifest."""

    rows: list[dict[str, str]] = []
    for manifest_path in manifest_paths:
        path = Path(manifest_path)
        if not path.exists():
            rows.append(_missing_manifest_row(path))
            continue
        manifest = _load_json_object(path)
        rows.extend(_rows_for_manifest(path, manifest))
    return rows


def write_graph_scale_manifest_audit(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_GRAPH_SCALE_MANIFEST_AUDIT_PATH,
    manifest_path: str | Path = DEFAULT_GRAPH_SCALE_MANIFEST_AUDIT_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_GRAPH_SCALE_MANIFEST_AUDIT_DOC_PATH,
    audited_manifest_paths: Sequence[str | Path] = DEFAULT_AUDITED_GRAPH_SCALE_MANIFEST_PATHS,
) -> dict[str, Any]:
    """Write graph-scale manifest coverage CSV, manifest, and Markdown doc."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    doc = Path(doc_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    doc.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=GRAPH_SCALE_MANIFEST_AUDIT_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    column: str(row.get(column, ""))
                    for column in GRAPH_SCALE_MANIFEST_AUDIT_COLUMNS
                }
            )

    summary = build_graph_scale_manifest_audit_manifest(
        rows=rows,
        output_path=output,
        manifest_path=manifest,
        doc_path=doc,
        audited_manifest_paths=audited_manifest_paths,
    )
    manifest.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    doc.write_text(
        build_graph_scale_manifest_audit_markdown(summary, rows=rows),
        encoding="utf-8",
    )
    return summary


def build_graph_scale_manifest_audit_manifest(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_GRAPH_SCALE_MANIFEST_AUDIT_PATH,
    manifest_path: str | Path = DEFAULT_GRAPH_SCALE_MANIFEST_AUDIT_MANIFEST_PATH,
    doc_path: str | Path = DEFAULT_GRAPH_SCALE_MANIFEST_AUDIT_DOC_PATH,
    audited_manifest_paths: Sequence[str | Path] = DEFAULT_AUDITED_GRAPH_SCALE_MANIFEST_PATHS,
) -> dict[str, Any]:
    """Return a conservative summary for graph-scale manifest audit rows."""

    status_counts = _counts(row.get("coverage_status", "") for row in rows)
    family_counts = _counts(row.get("artifact_family", "") for row in rows)
    missing_or_incomplete = sum(
        1
        for row in rows
        if row.get("coverage_status")
        in {
            "missing_manifest",
            "missing_graph_scale",
            "incomplete_graph_scale",
        }
    )
    reduced_count = sum(
        1 for row in rows if _is_true(row.get("analysis_graph_reduced", ""))
    )
    return {
        "schema_version": 1,
        "result_scope": GRAPH_SCALE_MANIFEST_AUDIT_SCOPE,
        "claim_boundary": (
            "This audit checks whether generated scaffold manifests expose "
            "source and analysis graph-scale fields. It does not accept a "
            "graph-scale method, validate route sufficiency, calibrate inputs, "
            "or close final-study gates."
        ),
        "row_count": len(rows),
        "audited_manifest_count": len({_display_path(Path(path)) for path in audited_manifest_paths}),
        "coverage_status_counts": status_counts,
        "artifact_family_counts": family_counts,
        "missing_or_incomplete_row_count": missing_or_incomplete,
        "complete_graph_scale_row_count": len(rows) - missing_or_incomplete,
        "reduced_analysis_graph_row_count": reduced_count,
        "source_graph_node_counts": _unique_ints(
            row.get("source_graph_nodes", "") for row in rows
        ),
        "source_graph_edge_counts": _unique_ints(
            row.get("source_graph_edges", "") for row in rows
        ),
        "analysis_graph_node_counts": _unique_ints(
            row.get("analysis_graph_nodes", "") for row in rows
        ),
        "analysis_graph_edge_counts": _unique_ints(
            row.get("analysis_graph_edges", "") for row in rows
        ),
        "publication_ready": False,
        "can_mark_complete": False,
        "inputs": {
            "audited_manifests": [
                _display_path(Path(path)) for path in audited_manifest_paths
            ],
        },
        "outputs": {
            "csv": _display_path(Path(output_path)),
            "manifest": _display_path(Path(manifest_path)),
            "doc": _display_path(Path(doc_path)),
        },
        "review_items": [
            "confirm the source graph count is stable across pilot, sensitivity, statistics, and figure/table manifests",
            "review whether each reduced analysis graph is a final method or only a scaffold shortcut",
            "regenerate downstream manifests if a different graph-scale method is accepted",
            "record any accepted graph-scale decision only in data/manifests/graph_scale_acceptance.json",
        ],
    }


def build_graph_scale_manifest_audit_markdown(
    manifest: Mapping[str, Any],
    *,
    rows: Sequence[Mapping[str, str]],
) -> str:
    """Return a Markdown graph-scale manifest audit report."""

    lines = [
        "# Graph-Scale Manifest Audit",
        "",
        str(manifest.get("claim_boundary", GRAPH_SCALE_MANIFEST_AUDIT_SCOPE)),
        "",
        "## Summary",
        "",
        f"- Row count: {manifest.get('row_count', 0)}",
        f"- Audited manifest count: {manifest.get('audited_manifest_count', 0)}",
        f"- Missing or incomplete rows: {manifest.get('missing_or_incomplete_row_count', 0)}",
        f"- Reduced analysis graph rows: {manifest.get('reduced_analysis_graph_row_count', 0)}",
        f"- Source node counts: `{manifest.get('source_graph_node_counts', [])}`",
        f"- Analysis node counts: `{manifest.get('analysis_graph_node_counts', [])}`",
        f"- Coverage status counts: `{manifest.get('coverage_status_counts', {})}`",
        "",
        "## Rows",
        "",
        "| Manifest | Component | Family | Source | Analysis | Status | Required action |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        source = f"{row.get('source_graph_nodes', '')}/{row.get('source_graph_edges', '')}"
        analysis = f"{row.get('analysis_graph_nodes', '')}/{row.get('analysis_graph_edges', '')}"
        lines.append(
            "| {manifest_path} | {component} | {family} | {source} | {analysis} | {status} | {action} |".format(
                manifest_path=_cell(row.get("manifest_path", "")),
                component=_cell(row.get("component_id", "")),
                family=_cell(row.get("artifact_family", "")),
                source=_cell(source),
                analysis=_cell(analysis),
                status=_cell(row.get("coverage_status", "")),
                action=_cell(row.get("required_reviewer_action", "")),
            )
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- This packet is graph-scale visibility evidence only.",
            "- It does not decide whether the reduced corridor, multi-corridor candidate, or full graph is the accepted final method.",
            "- It cannot create or replace `data/manifests/graph_scale_acceptance.json`.",
            "",
        ]
    )
    return "\n".join(lines)


def _rows_for_manifest(path: Path, manifest: Mapping[str, Any]) -> list[dict[str, str]]:
    graph_scale = manifest.get("graph_scale")
    if _has_source_analysis(graph_scale):
        return [_row(path, "default", manifest, graph_scale)]

    source_graph_scale = manifest.get("source_graph_scale")
    if _has_source_analysis(source_graph_scale):
        return [_row(path, "default", manifest, source_graph_scale)]

    if isinstance(graph_scale, Mapping):
        rows = [
            _row(path, str(component_id), manifest, component)
            for component_id, component in graph_scale.items()
            if _has_source_analysis(component)
        ]
        if rows:
            return rows

    if _has_top_level_graph_scale(manifest):
        return [_row(path, "default", manifest, _top_level_graph_scale(manifest))]

    return [_missing_graph_scale_row(path, manifest)]


def _row(
    path: Path,
    component_id: str,
    manifest: Mapping[str, Any],
    graph_scale: Any,
) -> dict[str, str]:
    source = _mapping_value(graph_scale, "source")
    analysis = _mapping_value(graph_scale, "analysis")
    source_nodes = source.get("nodes", "")
    source_edges = source.get("edges", "")
    analysis_nodes = analysis.get("nodes", "")
    analysis_edges = analysis.get("edges", "")
    analysis_reduced = analysis.get("reduced", manifest.get("analysis_graph_reduced", ""))
    analysis_strategy = analysis.get(
        "strategy",
        manifest.get("analysis_graph_strategy", ""),
    )
    complete = (
        _positive_int(source_nodes)
        and _positive_int(source_edges)
        and _positive_int(analysis_nodes)
        and _positive_int(analysis_edges)
        and str(analysis_strategy).strip()
    )
    status = (
        _complete_status(analysis_reduced)
        if complete
        else "incomplete_graph_scale"
    )
    return {
        "manifest_path": _display_path(path),
        "component_id": component_id,
        "artifact_family": _artifact_family(path, manifest, component_id),
        "manifest_present": "true",
        "graph_scale_present": "true",
        "source_graph_nodes": str(source_nodes),
        "source_graph_edges": str(source_edges),
        "analysis_graph_nodes": str(analysis_nodes),
        "analysis_graph_edges": str(analysis_edges),
        "analysis_graph_reduced": _bool_text(analysis_reduced),
        "analysis_graph_strategy": str(analysis_strategy),
        "graph_source": str(manifest.get("graph_source", "")),
        "command": str(manifest.get("command", "")),
        "run_profile_or_method": _run_profile_or_method(manifest),
        "result_scope": str(manifest.get("result_scope", "")),
        "coverage_status": status,
        "required_reviewer_action": _required_action(status),
        "claim_boundary": GRAPH_SCALE_MANIFEST_AUDIT_SCOPE,
    }


def _missing_manifest_row(path: Path) -> dict[str, str]:
    return {
        "manifest_path": _display_path(path),
        "component_id": "default",
        "artifact_family": _artifact_family(path, {}, "default"),
        "manifest_present": "false",
        "graph_scale_present": "false",
        "source_graph_nodes": "",
        "source_graph_edges": "",
        "analysis_graph_nodes": "",
        "analysis_graph_edges": "",
        "analysis_graph_reduced": "",
        "analysis_graph_strategy": "",
        "graph_source": "",
        "command": "",
        "run_profile_or_method": "",
        "result_scope": "",
        "coverage_status": "missing_manifest",
        "required_reviewer_action": "regenerate the expected manifest before graph-scale review",
        "claim_boundary": GRAPH_SCALE_MANIFEST_AUDIT_SCOPE,
    }


def _missing_graph_scale_row(path: Path, manifest: Mapping[str, Any]) -> dict[str, str]:
    return {
        "manifest_path": _display_path(path),
        "component_id": "default",
        "artifact_family": _artifact_family(path, manifest, "default"),
        "manifest_present": "true",
        "graph_scale_present": "false",
        "source_graph_nodes": "",
        "source_graph_edges": "",
        "analysis_graph_nodes": "",
        "analysis_graph_edges": "",
        "analysis_graph_reduced": "",
        "analysis_graph_strategy": "",
        "graph_source": str(manifest.get("graph_source", "")),
        "command": str(manifest.get("command", "")),
        "run_profile_or_method": _run_profile_or_method(manifest),
        "result_scope": str(manifest.get("result_scope", "")),
        "coverage_status": "missing_graph_scale",
        "required_reviewer_action": "regenerate this manifest with source and analysis graph-scale fields",
        "claim_boundary": GRAPH_SCALE_MANIFEST_AUDIT_SCOPE,
    }


def _load_json_object(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _has_source_analysis(value: Any) -> bool:
    return (
        isinstance(value, Mapping)
        and isinstance(value.get("source"), Mapping)
        and isinstance(value.get("analysis"), Mapping)
    )


def _has_top_level_graph_scale(manifest: Mapping[str, Any]) -> bool:
    required = (
        "source_graph_nodes",
        "source_graph_edges",
        "graph_nodes",
        "graph_edges",
    )
    return any(key in manifest for key in required)


def _top_level_graph_scale(manifest: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source": {
            "nodes": manifest.get("source_graph_nodes", ""),
            "edges": manifest.get("source_graph_edges", ""),
        },
        "analysis": {
            "nodes": manifest.get("graph_nodes", ""),
            "edges": manifest.get("graph_edges", ""),
            "reduced": manifest.get("analysis_graph_reduced", ""),
            "strategy": manifest.get("analysis_graph_strategy", ""),
        },
    }


def _mapping_value(value: Any, key: str) -> Mapping[str, Any]:
    if isinstance(value, Mapping) and isinstance(value.get(key), Mapping):
        return value[key]
    return {}


def _complete_status(analysis_reduced: Any) -> str:
    if _is_true(analysis_reduced):
        return "complete_reduced_analysis_graph_recorded"
    if str(analysis_reduced).strip():
        return "complete_non_reduced_analysis_graph_recorded"
    return "complete_analysis_graph_recorded_reduction_unknown"


def _required_action(status: str) -> str:
    if status == "complete_reduced_analysis_graph_recorded":
        return (
            "review reduced/candidate graph method before graph-scale acceptance"
        )
    if status == "complete_non_reduced_analysis_graph_recorded":
        return "review full-graph runtime and result evidence before acceptance"
    if status == "complete_analysis_graph_recorded_reduction_unknown":
        return "review and record whether the analysis graph is reduced"
    return "regenerate manifest with complete source and analysis graph-scale fields"


def _artifact_family(path: Path, manifest: Mapping[str, Any], component_id: str) -> str:
    name = path.name
    command = str(manifest.get("command", ""))
    method = str(manifest.get("method", ""))
    if name == "figure_table_manifest.json":
        return f"figure_table_{component_id}"
    if name.endswith("_statistics_manifest.json"):
        return "pilot_statistics"
    if "morris" in name or method == "salib_morris":
        return "morris_sensitivity"
    if "sensitivity" in name or "run_sensitivity" in command:
        return "deterministic_sensitivity"
    if name.startswith("pilot_"):
        return "pilot_experiment"
    return "unknown"


def _run_profile_or_method(manifest: Mapping[str, Any]) -> str:
    run_profile = str(manifest.get("run_profile", "")).strip()
    method = str(manifest.get("method", "")).strip()
    source_run_profile = str(manifest.get("source_run_profile", "")).strip()
    return run_profile or method or source_run_profile


def _counts(values: Sequence[str] | Any) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value).strip() or "blank"
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _unique_ints(values: Any) -> list[int]:
    output: set[int] = set()
    for value in values:
        number = _int_value(value)
        if number is not None:
            output.add(number)
    return sorted(output)


def _positive_int(value: Any) -> bool:
    number = _int_value(value)
    return number is not None and number > 0


def _int_value(value: Any) -> int | None:
    try:
        text = str(value).strip()
        if not text:
            return None
        return int(float(text))
    except (TypeError, ValueError):
        return None


def _is_true(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def _bool_text(value: Any) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    text = str(value).strip()
    if not text:
        return ""
    return str(_is_true(text)).lower()


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


__all__ = [
    "DEFAULT_AUDITED_GRAPH_SCALE_MANIFEST_PATHS",
    "DEFAULT_GRAPH_SCALE_MANIFEST_AUDIT_DOC_PATH",
    "DEFAULT_GRAPH_SCALE_MANIFEST_AUDIT_MANIFEST_PATH",
    "DEFAULT_GRAPH_SCALE_MANIFEST_AUDIT_PATH",
    "GRAPH_SCALE_MANIFEST_AUDIT_COLUMNS",
    "GRAPH_SCALE_MANIFEST_AUDIT_SCOPE",
    "build_graph_scale_manifest_audit_manifest",
    "build_graph_scale_manifest_audit_markdown",
    "build_graph_scale_manifest_audit_rows",
    "write_graph_scale_manifest_audit",
]
