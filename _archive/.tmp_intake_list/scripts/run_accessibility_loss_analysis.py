"""Regenerate route accessibility-loss diagnostics for the pilot scaffold."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys

import yaml


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld import build_simulator_graph, load_graphml  # noqa: E402
from src.realworld.accessibility import (  # noqa: E402
    ACCESSIBILITY_CSV_FIELDS,
    evaluate_accessibility_loss,
    records_to_csv_rows,
    summarize_accessibility_loss,
)


DEFAULT_REGION_PATH = ROOT / "data" / "regions" / "pilot_region.yaml"
DEFAULT_CACHE_PATH = ROOT / "data" / "cache" / "pilot_region_road.graphml"
DEFAULT_OUTPUT_PATH = ROOT / "data" / "validation" / "accessibility_loss.csv"
DEFAULT_SUMMARY_PATH = ROOT / "data" / "validation" / "accessibility_loss_summary.md"


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    result = run_accessibility_loss_analysis(
        region_path=args.region_path,
        cache_path=args.cache_path,
        output_path=args.output_path,
        summary_path=args.summary_path,
    )
    print(
        "Accessibility-loss diagnostics written: "
        f"{result['row_count']} rows, routes={result['route_count']}, "
        f"disconnected={result['disconnected_count']}"
    )
    print(f"csv: {result['output_path']}")
    print(f"summary: {result['summary_path']}")
    return 0


def run_accessibility_loss_analysis(
    *,
    region_path: str | Path = DEFAULT_REGION_PATH,
    cache_path: str | Path = DEFAULT_CACHE_PATH,
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
    summary_path: str | Path = DEFAULT_SUMMARY_PATH,
) -> dict:
    """Load cached pilot graph and write route-level edge-removal diagnostics."""

    region = _load_yaml_mapping(Path(region_path))
    road_graph = load_graphml(cache_path, normalize=True)
    simulator_graph = build_simulator_graph(road_graph, region)
    records = evaluate_accessibility_loss(
        simulator_graph,
        region_id=str(region["region_id"]),
    )
    summary = summarize_accessibility_loss(records)

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=ACCESSIBILITY_CSV_FIELDS)
        writer.writeheader()
        writer.writerows(records_to_csv_rows(records))

    summary_file = Path(summary_path)
    summary_file.parent.mkdir(parents=True, exist_ok=True)
    summary_file.write_text(
        _summary_text(
            region_id=str(region["region_id"]),
            cache_path=Path(cache_path),
            output_path=output,
            summary=summary,
            graph_nodes=simulator_graph.number_of_nodes(),
            graph_edges=simulator_graph.number_of_edges(),
        ),
        encoding="utf-8",
    )

    return {
        "row_count": summary["row_count"],
        "route_count": summary["route_count"],
        "disconnected_count": summary["disconnected_count"],
        "criticality_counts": summary["criticality_counts"],
        "output_path": str(output),
        "summary_path": str(summary_file),
    }


def _summary_text(
    *,
    region_id: str,
    cache_path: Path,
    output_path: Path,
    summary: dict,
    graph_nodes: int,
    graph_edges: int,
) -> str:
    counts = summary["criticality_counts"]
    lines = [
        "# Pilot Accessibility-Loss Diagnostic Summary",
        "",
        f"Region ID: `{region_id}`",
        "",
        "Evidence class: scaffold route-fragility diagnostic. This is not",
        "calibrated real-world accessibility evidence and is not an operational",
        "routing recommendation.",
        "",
        "## Inputs",
        "",
        "- Region spec: `data/regions/pilot_region.yaml`",
        f"- Cached road graph: `{_display_path(cache_path)}`",
        "- Diagnostic helper: `src/realworld/accessibility.py`",
        f"- Accessibility-loss table: `{_display_path(output_path)}`",
        "",
        "## Current Snapshot Results",
        "",
        f"- Adapted graph nodes: {graph_nodes}",
        f"- Adapted graph edges: {graph_edges}",
        f"- Diagnostic rows: {summary['row_count']}",
        f"- Routes checked: {summary['route_count']}",
        f"- Route IDs: {', '.join(summary['route_ids'])}",
        f"- Disconnected edge-removal cases: {summary['disconnected_count']}",
        "",
        "Criticality counts:",
        "",
    ]
    for key, value in counts.items():
        lines.append(f"- `{key}`: {value}")
    lines.extend(
        [
            "",
            "## Interpretation Boundary",
            "",
            "- Each row removes one directed edge from the baseline shortest-time road",
            "  path and recomputes the road route.",
            "- The diagnostic identifies where the current adapted graph is fragile to",
            "  local link removal.",
            "- It does not assign outage probabilities, traffic reassignment behavior,",
            "  emergency control behavior, or real accessibility loss.",
            "- Final manuscript claims still require accepted graph-scale, road-input,",
            "  validation, and experiment gates.",
            "",
            "## Review Items",
            "",
        ]
    )
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
    return parser.parse_args(argv)


def _load_yaml_mapping(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        value = yaml.safe_load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a mapping")
    return value


def _display_path(path: str | Path) -> str:
    filepath = Path(path)
    try:
        return filepath.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return filepath.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
