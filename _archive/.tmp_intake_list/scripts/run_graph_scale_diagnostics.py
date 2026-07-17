"""Regenerate graph-scale diagnostics for the reduced pilot corridor."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.graph_scale_diagnostics import (  # noqa: E402
    GRAPH_SCALE_ALTERNATE_ROUTE_CSV_FIELDS,
    GRAPH_SCALE_CSV_FIELDS,
    compare_graph_scale_alternate_routes,
    compare_graph_scale_routes,
    graph_scale_alternate_records_to_csv_rows,
    graph_scale_records_to_csv_rows,
    summarize_graph_scale_alternate_route_comparisons,
    summarize_graph_scale_route_comparisons,
)
from src.realworld.pilot_experiments import (  # noqa: E402
    DEFAULT_CACHE_PATH,
    DEFAULT_REGION_PATH,
    load_pilot_inputs,
    pilot_experiment_multi_corridor_subgraph,
)


DEFAULT_OUTPUT_PATH = ROOT / "data" / "validation" / "graph_scale_route_comparison.csv"
DEFAULT_SUMMARY_PATH = (
    ROOT / "data" / "validation" / "graph_scale_route_comparison_summary.md"
)
DEFAULT_ALTERNATE_OUTPUT_PATH = (
    ROOT / "data" / "validation" / "graph_scale_alternate_routes.csv"
)
DEFAULT_ALTERNATE_SUMMARY_PATH = (
    ROOT / "data" / "validation" / "graph_scale_alternate_routes_summary.md"
)
DEFAULT_MULTI_CORRIDOR_OUTPUT_PATH = (
    ROOT / "data" / "validation" / "graph_scale_multi_corridor_routes.csv"
)
DEFAULT_MULTI_CORRIDOR_SUMMARY_PATH = (
    ROOT / "data" / "validation" / "graph_scale_multi_corridor_routes_summary.md"
)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    result = run_graph_scale_diagnostics(
        region_path=args.region_path,
        cache_path=args.cache_path,
        output_path=args.output_path,
        summary_path=args.summary_path,
        alternate_output_path=args.alternate_output_path,
        alternate_summary_path=args.alternate_summary_path,
        alternate_path_count=args.alternate_path_count,
        multi_corridor_output_path=args.multi_corridor_output_path,
        multi_corridor_summary_path=args.multi_corridor_summary_path,
    )
    print(
        "Graph-scale route diagnostics written: "
        f"{result['row_count']} rows, status={result['status_counts']}"
    )
    print(
        "Graph-scale alternate-route diagnostics written: "
        f"{result['alternate_row_count']} rows, "
        f"status={result['alternate_status_counts']}"
    )
    print(
        "Graph-scale multi-corridor diagnostics written: "
        f"{result['multi_corridor_row_count']} rows, "
        f"status={result['multi_corridor_status_counts']}"
    )
    print(f"csv: {result['output_path']}")
    print(f"summary: {result['summary_path']}")
    print(f"alternate csv: {result['alternate_output_path']}")
    print(f"alternate summary: {result['alternate_summary_path']}")
    print(f"multi-corridor csv: {result['multi_corridor_output_path']}")
    print(f"multi-corridor summary: {result['multi_corridor_summary_path']}")
    return 0


def run_graph_scale_diagnostics(
    *,
    region_path: str | Path = DEFAULT_REGION_PATH,
    cache_path: str | Path = DEFAULT_CACHE_PATH,
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
    summary_path: str | Path = DEFAULT_SUMMARY_PATH,
    alternate_output_path: str | Path = DEFAULT_ALTERNATE_OUTPUT_PATH,
    alternate_summary_path: str | Path = DEFAULT_ALTERNATE_SUMMARY_PATH,
    alternate_path_count: int = 3,
    multi_corridor_output_path: str | Path = DEFAULT_MULTI_CORRIDOR_OUTPUT_PATH,
    multi_corridor_summary_path: str | Path = DEFAULT_MULTI_CORRIDOR_SUMMARY_PATH,
) -> dict:
    """Load full and reduced pilot graphs, then write graph-scale diagnostics."""

    full_inputs = load_pilot_inputs(
        region_path=region_path,
        cache_path=cache_path,
        reduce_graph=False,
    )
    reduced_inputs = load_pilot_inputs(
        region_path=region_path,
        cache_path=cache_path,
        reduce_graph=True,
    )
    records = compare_graph_scale_routes(
        full_inputs.graph,
        reduced_inputs.graph,
        region_id=full_inputs.region_id,
    )
    summary = summarize_graph_scale_route_comparisons(records)
    alternate_records = compare_graph_scale_alternate_routes(
        full_inputs.graph,
        reduced_inputs.graph,
        region_id=full_inputs.region_id,
        path_count=alternate_path_count,
    )
    alternate_summary = summarize_graph_scale_alternate_route_comparisons(
        alternate_records,
    )
    multi_corridor_graph = pilot_experiment_multi_corridor_subgraph(
        full_inputs.graph,
        path_count=alternate_path_count,
    )
    multi_corridor_records = compare_graph_scale_alternate_routes(
        full_inputs.graph,
        multi_corridor_graph,
        region_id=full_inputs.region_id,
        path_count=alternate_path_count,
    )
    multi_corridor_summary = summarize_graph_scale_alternate_route_comparisons(
        multi_corridor_records,
    )

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=GRAPH_SCALE_CSV_FIELDS)
        writer.writeheader()
        writer.writerows(graph_scale_records_to_csv_rows(records))

    summary_file = Path(summary_path)
    summary_file.parent.mkdir(parents=True, exist_ok=True)
    summary_file.write_text(
        _summary_text(
            region_id=full_inputs.region_id,
            cache_path=Path(cache_path),
            output_path=output,
            summary=summary,
            full_nodes=full_inputs.graph.number_of_nodes(),
            full_edges=full_inputs.graph.number_of_edges(),
            reduced_nodes=reduced_inputs.graph.number_of_nodes(),
            reduced_edges=reduced_inputs.graph.number_of_edges(),
        ),
        encoding="utf-8",
    )
    alternate_output = Path(alternate_output_path)
    alternate_output.parent.mkdir(parents=True, exist_ok=True)
    with alternate_output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=GRAPH_SCALE_ALTERNATE_ROUTE_CSV_FIELDS,
        )
        writer.writeheader()
        writer.writerows(
            graph_scale_alternate_records_to_csv_rows(alternate_records)
        )

    alternate_summary_file = Path(alternate_summary_path)
    alternate_summary_file.parent.mkdir(parents=True, exist_ok=True)
    alternate_summary_file.write_text(
        _alternate_summary_text(
            region_id=full_inputs.region_id,
            cache_path=Path(cache_path),
            output_path=alternate_output,
            summary=alternate_summary,
            full_nodes=full_inputs.graph.number_of_nodes(),
            full_edges=full_inputs.graph.number_of_edges(),
            reduced_nodes=reduced_inputs.graph.number_of_nodes(),
            reduced_edges=reduced_inputs.graph.number_of_edges(),
            title="Graph-Scale Alternate Route Summary",
            evidence_class="graph-scale alternate-route sensitivity diagnostic",
            graph_label="Reduced analysis corridor",
        ),
        encoding="utf-8",
    )
    multi_corridor_output = Path(multi_corridor_output_path)
    multi_corridor_output.parent.mkdir(parents=True, exist_ok=True)
    with multi_corridor_output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=GRAPH_SCALE_ALTERNATE_ROUTE_CSV_FIELDS,
        )
        writer.writeheader()
        writer.writerows(
            graph_scale_alternate_records_to_csv_rows(multi_corridor_records)
        )

    multi_corridor_summary_file = Path(multi_corridor_summary_path)
    multi_corridor_summary_file.parent.mkdir(parents=True, exist_ok=True)
    multi_corridor_summary_file.write_text(
        _alternate_summary_text(
            region_id=full_inputs.region_id,
            cache_path=Path(cache_path),
            output_path=multi_corridor_output,
            summary=multi_corridor_summary,
            full_nodes=full_inputs.graph.number_of_nodes(),
            full_edges=full_inputs.graph.number_of_edges(),
            reduced_nodes=multi_corridor_graph.number_of_nodes(),
            reduced_edges=multi_corridor_graph.number_of_edges(),
            title="Graph-Scale Multi-Corridor Candidate Summary",
            evidence_class="graph-scale multi-corridor candidate diagnostic",
            graph_label="Multi-corridor candidate graph",
        ),
        encoding="utf-8",
    )
    return {
        "row_count": summary["row_count"],
        "status_counts": summary["status_counts"],
        "all_routes_available": summary["all_routes_available"],
        "all_time_paths_preserved": summary["all_time_paths_preserved"],
        "all_distance_paths_preserved": summary["all_distance_paths_preserved"],
        "output_path": str(output),
        "summary_path": str(summary_file),
        "alternate_row_count": alternate_summary["row_count"],
        "alternate_status_counts": alternate_summary["status_counts"],
        "all_rank_one_paths_preserved": alternate_summary[
            "all_rank_one_paths_preserved"
        ],
        "all_alternate_paths_preserved": alternate_summary[
            "all_alternate_paths_preserved"
        ],
        "alternate_output_path": str(alternate_output),
        "alternate_summary_path": str(alternate_summary_file),
        "multi_corridor_row_count": multi_corridor_summary["row_count"],
        "multi_corridor_status_counts": multi_corridor_summary["status_counts"],
        "all_multi_corridor_alternate_paths_preserved": multi_corridor_summary[
            "all_alternate_paths_preserved"
        ],
        "multi_corridor_output_path": str(multi_corridor_output),
        "multi_corridor_summary_path": str(multi_corridor_summary_file),
    }


def _summary_text(
    *,
    region_id: str,
    cache_path: Path,
    output_path: Path,
    summary: dict,
    full_nodes: int,
    full_edges: int,
    reduced_nodes: int,
    reduced_edges: int,
) -> str:
    counts = summary["status_counts"]
    lines = [
        "# Graph-Scale Route Comparison Summary",
        "",
        f"Region ID: `{region_id}`",
        "",
        "Evidence class: graph-scale scaffold diagnostic. This compares baseline",
        "shortest road routes on the full bus-practical graph and the reduced",
        "analysis corridor. It is not graph-scale acceptance and not calibrated",
        "real-world validation.",
        "",
        "## Inputs",
        "",
        "- Region spec: `data/regions/pilot_region.yaml`",
        f"- Cached road graph: `{_display_path(cache_path)}`",
        "- Diagnostic helper: `src/realworld/graph_scale_diagnostics.py`",
        f"- Route comparison table: `{_display_path(output_path)}`",
        "",
        "## Current Snapshot Results",
        "",
        f"- Full bus-practical graph nodes: {full_nodes}",
        f"- Full bus-practical graph edges: {full_edges}",
        f"- Reduced analysis corridor nodes: {reduced_nodes}",
        f"- Reduced analysis corridor edges: {reduced_edges}",
        f"- Route comparison rows: {summary['row_count']}",
        f"- Pass: {counts.get('pass', 0)}",
        f"- Warn: {counts.get('warn', 0)}",
        f"- Fail: {counts.get('fail', 0)}",
        f"- All routes available: {str(summary['all_routes_available']).lower()}",
        f"- All full shortest-time paths preserved: {str(summary['all_time_paths_preserved']).lower()}",
        f"- All full shortest-distance paths preserved: {str(summary['all_distance_paths_preserved']).lower()}",
        "",
        "## Interpretation Boundary",
        "",
        "- A pass means the reduced corridor preserves the current full-graph",
        "  baseline shortest-time route for a canonical road leg.",
        "- This diagnostic does not evaluate all alternate corridors, traffic",
        "  assignment, spillback, hazard exposure, or operational detours.",
        "- Final graph-scale claims still require",
        "  `data/manifests/graph_scale_acceptance.json` after review.",
        "",
        "## Review Items",
        "",
    ]
    for item in summary["review_items"]:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def _alternate_summary_text(
    *,
    region_id: str,
    cache_path: Path,
    output_path: Path,
    summary: dict,
    full_nodes: int,
    full_edges: int,
    reduced_nodes: int,
    reduced_edges: int,
    title: str,
    evidence_class: str,
    graph_label: str,
) -> str:
    counts = summary["status_counts"]
    lines = [
        f"# {title}",
        "",
        f"Region ID: `{region_id}`",
        "",
        f"Evidence class: {evidence_class}.",
        "This table compares top full-graph shortest-time route candidates with",
        f"the {graph_label.lower()}. It is not graph-scale acceptance and not calibrated",
        "real-world validation.",
        "",
        "## Inputs",
        "",
        "- Region spec: `data/regions/pilot_region.yaml`",
        f"- Cached road graph: `{_display_path(cache_path)}`",
        "- Diagnostic helper: `src/realworld/graph_scale_diagnostics.py`",
        f"- Alternate-route table: `{_display_path(output_path)}`",
        "",
        "## Current Snapshot Results",
        "",
        f"- Full bus-practical graph nodes: {full_nodes}",
        f"- Full bus-practical graph edges: {full_edges}",
        f"- {graph_label} nodes: {reduced_nodes}",
        f"- {graph_label} edges: {reduced_edges}",
        f"- Requested paths per route: {summary['requested_path_count']}",
        f"- Alternate-route rows: {summary['row_count']}",
        f"- Pass: {counts.get('pass', 0)}",
        f"- Warn: {counts.get('warn', 0)}",
        f"- Fail: {counts.get('fail', 0)}",
        f"- Rank-1 paths preserved: {summary['rank_one_exact_preserved_count']} / {summary['rank_one_path_count']}",
        f"- Alternate paths preserved: {summary['alternate_exact_preserved_count']} / {summary['alternate_path_count']}",
        f"- Minimum edge coverage in {graph_label.lower()}: {_format_summary_float(summary['min_edge_coverage_in_analysis'])}",
        f"- All analysis routes available: {str(summary['all_analysis_routes_available']).lower()}",
        f"- All rank-1 paths preserved: {str(summary['all_rank_one_paths_preserved']).lower()}",
        f"- All alternate paths preserved: {str(summary['all_alternate_paths_preserved']).lower()}",
        "",
        "## Interpretation Boundary",
        "",
        "- A pass means a full-graph candidate path is exactly present in the",
        f"  {graph_label.lower()}.",
        "- A warn for rank greater than 1 means an alternate full-graph path is",
        f"  omitted by the {graph_label.lower()} and should be treated as graph-scale",
        "  uncertainty.",
        "- This diagnostic does not perform dynamic traffic assignment, spillback,",
        "  hazard routing, or operational detour validation.",
        "- Final graph-scale claims still require",
        "  `data/manifests/graph_scale_acceptance.json` after review.",
        "",
        "## Review Items",
        "",
    ]
    for item in summary["review_items"]:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--region-path", type=Path, default=DEFAULT_REGION_PATH)
    parser.add_argument("--cache-path", type=Path, default=DEFAULT_CACHE_PATH)
    parser.add_argument("--output-path", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--summary-path", type=Path, default=DEFAULT_SUMMARY_PATH)
    parser.add_argument(
        "--alternate-output-path",
        type=Path,
        default=DEFAULT_ALTERNATE_OUTPUT_PATH,
    )
    parser.add_argument(
        "--alternate-summary-path",
        type=Path,
        default=DEFAULT_ALTERNATE_SUMMARY_PATH,
    )
    parser.add_argument("--alternate-path-count", type=int, default=3)
    parser.add_argument(
        "--multi-corridor-output-path",
        type=Path,
        default=DEFAULT_MULTI_CORRIDOR_OUTPUT_PATH,
    )
    parser.add_argument(
        "--multi-corridor-summary-path",
        type=Path,
        default=DEFAULT_MULTI_CORRIDOR_SUMMARY_PATH,
    )
    return parser.parse_args(argv)


def _display_path(path: str | Path) -> str:
    filepath = Path(path)
    try:
        return filepath.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return filepath.as_posix()


def _format_summary_float(value: object) -> str:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return "nan"
    return f"{parsed:.6f}"


if __name__ == "__main__":
    raise SystemExit(main())
