"""Graph-scale method review packet.

This module summarizes the current graph-scale choices into a small review
worksheet. It supports the graph-scale decision, but it is not an acceptance
record and does not validate calibrated real-world claims.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_GRAPH_SCALE_REVIEW_PACKET_PATH = (
    PROJECT_ROOT / "data" / "validation" / "graph_scale_review_packet.csv"
)
DEFAULT_GRAPH_SCALE_REVIEW_MANIFEST_PATH = (
    PROJECT_ROOT / "data" / "validation" / "graph_scale_review_manifest.json"
)
DEFAULT_ROUTE_COMPARISON_PATH = (
    PROJECT_ROOT / "data" / "validation" / "graph_scale_route_comparison.csv"
)
DEFAULT_ALTERNATE_ROUTE_PATH = (
    PROJECT_ROOT / "data" / "validation" / "graph_scale_alternate_routes.csv"
)
DEFAULT_MULTI_CORRIDOR_ROUTE_PATH = (
    PROJECT_ROOT / "data" / "validation" / "graph_scale_multi_corridor_routes.csv"
)
DEFAULT_PILOT_FULL_MANIFEST_PATH = (
    PROJECT_ROOT / "results" / "realworld_pilot" / "pilot_full_manifest.json"
)
DEFAULT_MULTI_CORRIDOR_MANIFEST_PATH = (
    PROJECT_ROOT
    / "results"
    / "realworld_pilot"
    / "pilot_multi_corridor_manifest.json"
)
DEFAULT_MULTI_CORRIDOR_FULL_MANIFEST_PATH = (
    PROJECT_ROOT
    / "results"
    / "realworld_pilot"
    / "pilot_multi_corridor_full_manifest.json"
)

GRAPH_SCALE_REVIEW_SCOPE = (
    "graph_scale_method_review_packet_not_graph_scale_acceptance"
)
GRAPH_SCALE_REVIEW_COLUMNS: tuple[str, ...] = (
    "option_id",
    "option_label",
    "region_id",
    "source_graph_nodes",
    "source_graph_edges",
    "analysis_graph_nodes",
    "analysis_graph_edges",
    "analysis_graph_reduced",
    "diagnostic_route_rows",
    "diagnostic_route_pass",
    "diagnostic_route_warn",
    "diagnostic_route_fail",
    "alternate_route_rows",
    "alternate_route_pass",
    "alternate_route_warn",
    "alternate_route_fail",
    "rank_one_paths_preserved",
    "alternate_paths_preserved",
    "experiment_run_profile",
    "experiment_row_count",
    "experiment_summary_row_count",
    "available_evidence",
    "required_before_final_use",
    "publication_use_status",
    "claim_boundary",
)


def build_graph_scale_review_rows(
    *,
    route_comparison_path: str | Path = DEFAULT_ROUTE_COMPARISON_PATH,
    alternate_route_path: str | Path = DEFAULT_ALTERNATE_ROUTE_PATH,
    multi_corridor_route_path: str | Path = DEFAULT_MULTI_CORRIDOR_ROUTE_PATH,
    pilot_full_manifest_path: str | Path = DEFAULT_PILOT_FULL_MANIFEST_PATH,
    multi_corridor_manifest_path: str | Path = DEFAULT_MULTI_CORRIDOR_MANIFEST_PATH,
    multi_corridor_full_manifest_path: str
    | Path = DEFAULT_MULTI_CORRIDOR_FULL_MANIFEST_PATH,
) -> list[dict[str, str]]:
    """Return graph-scale option review rows from current scaffold artifacts."""

    pilot_full = _load_json_object(pilot_full_manifest_path)
    multi_corridor = _load_json_object(multi_corridor_manifest_path)
    multi_corridor_full = _load_json_object(multi_corridor_full_manifest_path)
    route_summary = _status_summary(_read_csv_rows(route_comparison_path))
    alternate_summary = _status_summary(_read_csv_rows(alternate_route_path))
    multi_summary = _status_summary(_read_csv_rows(multi_corridor_route_path))

    return [
        _current_reduced_row(pilot_full, route_summary, alternate_summary),
        _multi_corridor_row(multi_corridor, multi_summary),
        _multi_corridor_full_row(multi_corridor_full, multi_summary),
        _full_graph_row(pilot_full),
    ]


def write_graph_scale_review_packet(
    *,
    rows: Sequence[Mapping[str, str]],
    output_path: str | Path = DEFAULT_GRAPH_SCALE_REVIEW_PACKET_PATH,
    manifest_path: str | Path = DEFAULT_GRAPH_SCALE_REVIEW_MANIFEST_PATH,
) -> dict[str, Any]:
    """Write the graph-scale review packet and conservative manifest."""

    output = Path(output_path)
    manifest = Path(manifest_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=GRAPH_SCALE_REVIEW_COLUMNS,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)

    value = {
        "schema_version": 1,
        "result_scope": GRAPH_SCALE_REVIEW_SCOPE,
        "outputs": {
            "graph_scale_review_packet": _display_path(output),
            "manifest": _display_path(manifest),
        },
        "row_count": len(rows),
        "option_ids": [row["option_id"] for row in rows],
        "publication_ready": False,
        "claim_boundary": (
            "This packet compares graph-scale method options for review. It "
            "does not accept a graph-scale method, validate regional traffic "
            "behavior, or authorize final-study claims."
        ),
        "review_items": [
            "decide whether the 118-node reduced corridor is an acceptable final method or only a smoke shortcut",
            "if the 164-node multi-corridor candidate is selected, review the full-profile candidate output and regenerate sensitivity/figure/table outputs on the accepted graph",
            "review the full-scale multi-corridor candidate output before treating it as sufficient graph-scale evidence",
            "review the current-vs-candidate result comparison before interpreting graph-choice-sensitive scenarios",
            "if the full bus-practical graph is selected, generate full experiment runtime and result evidence",
            "record the reviewed decision only in data/manifests/graph_scale_acceptance.json",
        ],
    }
    with manifest.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return value


def _current_reduced_row(
    manifest: Mapping[str, Any],
    route_summary: Mapping[str, Any],
    alternate_summary: Mapping[str, Any],
) -> dict[str, str]:
    graph_scale = _graph_scale(manifest)
    analysis = graph_scale["analysis"]
    source = graph_scale["source"]
    return {
        "option_id": "current_reduced_corridor",
        "option_label": "Current 118-node reduced analysis corridor",
        "region_id": str(manifest.get("region_id", "")),
        "source_graph_nodes": str(source.get("nodes", "")),
        "source_graph_edges": str(source.get("edges", "")),
        "analysis_graph_nodes": str(analysis.get("nodes", "")),
        "analysis_graph_edges": str(analysis.get("edges", "")),
        "analysis_graph_reduced": _bool_text(analysis.get("reduced", True)),
        "diagnostic_route_rows": str(route_summary["row_count"]),
        "diagnostic_route_pass": str(route_summary["status_counts"].get("pass", 0)),
        "diagnostic_route_warn": str(route_summary["status_counts"].get("warn", 0)),
        "diagnostic_route_fail": str(route_summary["status_counts"].get("fail", 0)),
        "alternate_route_rows": str(alternate_summary["row_count"]),
        "alternate_route_pass": str(alternate_summary["status_counts"].get("pass", 0)),
        "alternate_route_warn": str(alternate_summary["status_counts"].get("warn", 0)),
        "alternate_route_fail": str(alternate_summary["status_counts"].get("fail", 0)),
        "rank_one_paths_preserved": _bool_text(
            alternate_summary["all_rank_one_paths_preserved"]
        ),
        "alternate_paths_preserved": _bool_text(
            alternate_summary["all_alternate_paths_preserved"]
        ),
        "experiment_run_profile": str(manifest.get("run_profile", "")),
        "experiment_row_count": str(manifest.get("row_count", "")),
        "experiment_summary_row_count": str(manifest.get("summary_row_count", "")),
        "available_evidence": (
            "baseline route parity passes; alternate-route diagnostic has "
            "warning rows; full pilot scaffold outputs exist"
        ),
        "required_before_final_use": (
            "review whether omitted alternate paths are immaterial, or replace "
            "with multi-corridor/full-graph method"
        ),
        "publication_use_status": "blocked_until_graph_scale_acceptance",
        "claim_boundary": GRAPH_SCALE_REVIEW_SCOPE,
    }


def _multi_corridor_row(
    manifest: Mapping[str, Any],
    route_summary: Mapping[str, Any],
) -> dict[str, str]:
    graph_scale = _graph_scale(manifest)
    analysis = graph_scale["analysis"]
    source = graph_scale["source"]
    return {
        "option_id": "multi_corridor_candidate",
        "option_label": "164-node multi-corridor candidate graph",
        "region_id": str(manifest.get("region_id", "")),
        "source_graph_nodes": str(source.get("nodes", "")),
        "source_graph_edges": str(source.get("edges", "")),
        "analysis_graph_nodes": str(analysis.get("nodes", "")),
        "analysis_graph_edges": str(analysis.get("edges", "")),
        "analysis_graph_reduced": _bool_text(analysis.get("reduced", True)),
        "diagnostic_route_rows": "",
        "diagnostic_route_pass": "",
        "diagnostic_route_warn": "",
        "diagnostic_route_fail": "",
        "alternate_route_rows": str(route_summary["row_count"]),
        "alternate_route_pass": str(route_summary["status_counts"].get("pass", 0)),
        "alternate_route_warn": str(route_summary["status_counts"].get("warn", 0)),
        "alternate_route_fail": str(route_summary["status_counts"].get("fail", 0)),
        "rank_one_paths_preserved": _bool_text(
            route_summary["all_rank_one_paths_preserved"]
        ),
        "alternate_paths_preserved": _bool_text(
            route_summary["all_alternate_paths_preserved"]
        ),
        "experiment_run_profile": str(manifest.get("run_profile", "")),
        "experiment_row_count": str(manifest.get("row_count", "")),
        "experiment_summary_row_count": str(manifest.get("summary_row_count", "")),
        "available_evidence": (
            "top-3 route candidates are preserved; small separated candidate "
            "experiment output exists"
        ),
        "required_before_final_use": (
            "regenerate full pilot, sensitivity, figures, tables, and "
            "manuscript interpretation on this graph if selected"
        ),
        "publication_use_status": "candidate_blocked_until_regeneration_and_acceptance",
        "claim_boundary": GRAPH_SCALE_REVIEW_SCOPE,
    }


def _multi_corridor_full_row(
    manifest: Mapping[str, Any],
    route_summary: Mapping[str, Any],
) -> dict[str, str]:
    graph_scale = _graph_scale(manifest)
    analysis = graph_scale["analysis"]
    source = graph_scale["source"]
    return {
        "option_id": "multi_corridor_full_candidate",
        "option_label": "164-node multi-corridor full-profile candidate graph",
        "region_id": str(manifest.get("region_id", "")),
        "source_graph_nodes": str(source.get("nodes", "")),
        "source_graph_edges": str(source.get("edges", "")),
        "analysis_graph_nodes": str(analysis.get("nodes", "")),
        "analysis_graph_edges": str(analysis.get("edges", "")),
        "analysis_graph_reduced": _bool_text(analysis.get("reduced", True)),
        "diagnostic_route_rows": "",
        "diagnostic_route_pass": "",
        "diagnostic_route_warn": "",
        "diagnostic_route_fail": "",
        "alternate_route_rows": str(route_summary["row_count"]),
        "alternate_route_pass": str(route_summary["status_counts"].get("pass", 0)),
        "alternate_route_warn": str(route_summary["status_counts"].get("warn", 0)),
        "alternate_route_fail": str(route_summary["status_counts"].get("fail", 0)),
        "rank_one_paths_preserved": _bool_text(
            route_summary["all_rank_one_paths_preserved"]
        ),
        "alternate_paths_preserved": _bool_text(
            route_summary["all_alternate_paths_preserved"]
        ),
        "experiment_run_profile": str(manifest.get("run_profile", "")),
        "experiment_row_count": str(manifest.get("row_count", "")),
        "experiment_summary_row_count": str(manifest.get("summary_row_count", "")),
        "available_evidence": (
            "top-3 route candidates are preserved; full scenario-policy-seed "
            "candidate output exists on the multi-corridor graph"
        ),
        "required_before_final_use": (
            "review result differences against the current full pilot, decide "
            "whether this graph-scale abstraction is acceptable, then "
            "regenerate sensitivity, figures, tables, and manuscript "
            "interpretation on the accepted method"
        ),
        "publication_use_status": "candidate_blocked_until_review_and_acceptance",
        "claim_boundary": GRAPH_SCALE_REVIEW_SCOPE,
    }


def _full_graph_row(manifest: Mapping[str, Any]) -> dict[str, str]:
    graph_scale = _graph_scale(manifest)
    source = graph_scale["source"]
    return {
        "option_id": "full_bus_practical_graph",
        "option_label": "Full bus-practical cached graph",
        "region_id": str(manifest.get("region_id", "")),
        "source_graph_nodes": str(source.get("nodes", "")),
        "source_graph_edges": str(source.get("edges", "")),
        "analysis_graph_nodes": str(source.get("nodes", "")),
        "analysis_graph_edges": str(source.get("edges", "")),
        "analysis_graph_reduced": "false",
        "diagnostic_route_rows": "",
        "diagnostic_route_pass": "",
        "diagnostic_route_warn": "",
        "diagnostic_route_fail": "",
        "alternate_route_rows": "",
        "alternate_route_pass": "",
        "alternate_route_warn": "",
        "alternate_route_fail": "",
        "rank_one_paths_preserved": "true",
        "alternate_paths_preserved": "true",
        "experiment_run_profile": "full_graph_smoke_only",
        "experiment_row_count": "0",
        "experiment_summary_row_count": "0",
        "available_evidence": (
            "full graph loads and smoke runs, but full scenario-policy-seed "
            "outputs have not been generated on the full graph"
        ),
        "required_before_final_use": (
            "establish runtime budget, generate full outputs or accepted sample "
            "strategy, then review validation and sensitivity on full graph"
        ),
        "publication_use_status": "blocked_until_full_graph_experiment_evidence",
        "claim_boundary": GRAPH_SCALE_REVIEW_SCOPE,
    }


def _status_summary(rows: Sequence[Mapping[str, str]]) -> dict[str, Any]:
    status_counts = {"pass": 0, "warn": 0, "fail": 0}
    for row in rows:
        status = str(row.get("status", "")).strip().lower()
        if status:
            status_counts[status] = status_counts.get(status, 0) + 1
    rank_one_rows = [
        row for row in rows if str(row.get("full_route_rank", "")).strip() == "1"
    ]
    alternate_rows = [
        row
        for row in rows
        if _positive_int(row.get("full_route_rank")) is not None
        and _positive_int(row.get("full_route_rank")) > 1
    ]
    return {
        "row_count": len(rows),
        "status_counts": status_counts,
        "all_rank_one_paths_preserved": bool(rank_one_rows)
        and all(_true(row.get("exact_full_path_present_in_analysis")) for row in rank_one_rows),
        "all_alternate_paths_preserved": bool(alternate_rows)
        and all(_true(row.get("exact_full_path_present_in_analysis")) for row in alternate_rows),
    }


def _graph_scale(manifest: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    raw = manifest.get("graph_scale", {})
    if not isinstance(raw, Mapping):
        raw = {}
    source = raw.get("source", {})
    analysis = raw.get("analysis", {})
    if not isinstance(source, Mapping):
        source = {}
    if not isinstance(analysis, Mapping):
        analysis = {}
    return {"source": source, "analysis": analysis}


def _read_csv_rows(path: str | Path) -> list[dict[str, str]]:
    csv_path = Path(path)
    if not csv_path.exists():
        return []
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _load_json_object(path: str | Path) -> dict[str, Any]:
    json_path = Path(path)
    if not json_path.exists():
        return {}
    with json_path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    return value if isinstance(value, dict) else {}


def _true(value: object) -> bool:
    return str(value).strip().lower() == "true"


def _positive_int(value: object) -> int | None:
    try:
        parsed = int(str(value).strip())
    except (TypeError, ValueError):
        return None
    return parsed if parsed > 0 else None


def _bool_text(value: object) -> str:
    return str(bool(value)).lower()


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


__all__ = [
    "DEFAULT_GRAPH_SCALE_REVIEW_MANIFEST_PATH",
    "DEFAULT_GRAPH_SCALE_REVIEW_PACKET_PATH",
    "DEFAULT_MULTI_CORRIDOR_FULL_MANIFEST_PATH",
    "DEFAULT_MULTI_CORRIDOR_MANIFEST_PATH",
    "GRAPH_SCALE_REVIEW_COLUMNS",
    "GRAPH_SCALE_REVIEW_SCOPE",
    "build_graph_scale_review_rows",
    "write_graph_scale_review_packet",
]
