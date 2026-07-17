"""Regenerate offline pilot route plausibility outputs."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
import sys

import yaml


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld import build_simulator_graph, load_graphml
from src.realworld.plausibility import (
    BENCHMARK_CSV_FIELDS,
    CSV_FIELDS,
    benchmark_records_to_csv_rows,
    benchmark_status_counts,
    build_fallback_route_benchmarks,
    evaluate_external_route_benchmarks,
    evaluate_graph_plausibility,
    records_to_csv_rows,
    status_counts,
)


DEFAULT_REGION_PATH = ROOT / "data" / "regions" / "pilot_region.yaml"
DEFAULT_CACHE_PATH = ROOT / "data" / "cache" / "pilot_region_road.graphml"
DEFAULT_OUTPUT_PATH = ROOT / "data" / "validation" / "route_plausibility.csv"
DEFAULT_BENCHMARK_OUTPUT_PATH = (
    ROOT / "data" / "validation" / "external_route_benchmarks.csv"
)
DEFAULT_SUMMARY_PATH = ROOT / "data" / "validation" / "validation_summary.md"


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    result = run_plausibility_validation(
        region_path=args.region_path,
        cache_path=args.cache_path,
        output_path=args.output_path,
        benchmark_output_path=args.benchmark_output_path,
        summary_path=args.summary_path,
    )
    print(
        "Pilot plausibility outputs written: "
        f"{result['row_count']} route rows, status={result['status_counts']}; "
        f"{result['benchmark_row_count']} benchmark rows, "
        f"benchmark_status={result['benchmark_status_counts']}"
    )
    print(f"csv: {result['output_path']}")
    print(f"benchmark_csv: {result['benchmark_output_path']}")
    print(f"summary: {result['summary_path']}")
    return 0


def run_plausibility_validation(
    *,
    region_path: str | Path = DEFAULT_REGION_PATH,
    cache_path: str | Path = DEFAULT_CACHE_PATH,
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
    benchmark_output_path: str | Path = DEFAULT_BENCHMARK_OUTPUT_PATH,
    summary_path: str | Path = DEFAULT_SUMMARY_PATH,
) -> dict:
    region = _load_yaml_mapping(Path(region_path))
    road_graph = load_graphml(cache_path, normalize=True)
    simulator_graph = build_simulator_graph(road_graph, region)
    records = evaluate_graph_plausibility(
        simulator_graph,
        region_id=str(region["region_id"]),
    )
    counts = status_counts(records)
    benchmark_records = evaluate_external_route_benchmarks(
        simulator_graph,
        build_fallback_route_benchmarks(simulator_graph),
        region_id=str(region["region_id"]),
    )
    benchmark_counts = benchmark_status_counts(benchmark_records)

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(records_to_csv_rows(records))

    benchmark_output = Path(benchmark_output_path)
    benchmark_output.parent.mkdir(parents=True, exist_ok=True)
    with benchmark_output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=BENCHMARK_CSV_FIELDS)
        writer.writeheader()
        writer.writerows(benchmark_records_to_csv_rows(benchmark_records))

    summary = Path(summary_path)
    summary.parent.mkdir(parents=True, exist_ok=True)
    summary.write_text(
        _summary_text(
            region_id=str(region["region_id"]),
            cache_path=Path(cache_path),
            output_path=output,
            benchmark_output_path=benchmark_output,
            row_count=len(records),
            counts=counts,
            benchmark_row_count=len(benchmark_records),
            benchmark_counts=benchmark_counts,
            graph_nodes=simulator_graph.number_of_nodes(),
            graph_edges=simulator_graph.number_of_edges(),
        ),
        encoding="utf-8",
    )
    return {
        "row_count": len(records),
        "status_counts": counts,
        "benchmark_row_count": len(benchmark_records),
        "benchmark_status_counts": benchmark_counts,
        "output_path": str(output),
        "benchmark_output_path": str(benchmark_output),
        "summary_path": str(summary),
    }


def _summary_text(
    *,
    region_id: str,
    cache_path: Path,
    output_path: Path,
    benchmark_output_path: Path,
    row_count: int,
    counts: dict[str, int],
    benchmark_row_count: int,
    benchmark_counts: dict[str, int],
    graph_nodes: int,
    graph_edges: int,
) -> str:
    return f"""# Pilot Route Plausibility Validation Summary

Region ID: `{region_id}`

Evidence class: scaffold/sanity evidence for the committed offline pilot graph.
This is not calibrated real-world validation and is not ground truth for
emergency operations or public transport service.

## Inputs

- Region spec: `data/regions/pilot_region.yaml`
- Cached road graph: `{_display_path(cache_path)}`
- Validation helper: `src/realworld/plausibility.py`
- Internal route plausibility table: `{_display_path(output_path)}`
- External/fallback benchmark table: `{_display_path(benchmark_output_path)}`

The adapted simulator graph filters pedestrian, cycling, platform,
construction, track, living-street, and service-only OSM geometries before
zone/rail-point snapping and route checks. These filtered geometries remain in
the raw cache for provenance, but they are not treated as bus-practical vehicle
routes.

The checks load the cached GraphML and adapted simulator graph only. They do not
call live OSM, OSRM, Valhalla, routingpy, R5, OpenTripPlanner, UXsim, or other
web/external routing services. The current benchmark layer uses an executable
documented fallback: endpoint-coordinate straight-line distance multiplied by a
route-class detour factor, then converted to time using coarse urban speed
assumptions. Cached OSRM/Valhalla/routingpy/R5/OpenTripPlanner/UXsim outputs
can replace the fallback later, but any such value remains a plausibility
benchmark and not ground truth.

## Current Snapshot Results

- Adapted graph nodes: {graph_nodes}
- Adapted graph edges: {graph_edges}
- Internal checks: {row_count}
- Pass: {counts.get("pass", 0)}
- Warn: {counts.get("warn", 0)}
- Fail: {counts.get("fail", 0)}
- Benchmark checks: {benchmark_row_count}
- Benchmark pass: {benchmark_counts.get("pass", 0)}
- Benchmark warn: {benchmark_counts.get("warn", 0)}
- Benchmark fail: {benchmark_counts.get("fail", 0)}

## Assumptions

- Route distance checks compare adapted graph path length with a straight-line
  coordinate lower bound from the public or synthetic scaffold points.
- Free-flow time checks use simulator `t0` values from the adapter and do not
  include congestion, dispatch waiting, transfer handling, or disruption.
- Implied speed checks use broad urban-road sanity ranges, not calibration.
- Connector checks use `connector_distance_m` metadata from the zone snapping
  layer.
- Road speed and capacity checks inspect non-connector road edges only and use
  coarse planning ranges.
- The benchmark table currently uses a documented executable fallback because
  no reviewed OSRM, Valhalla, routingpy, R5, OpenTripPlanner, or UXsim cache is
  committed. This gives Workstream 6 an explicit external-benchmark interface
  and reproducible comparison method without adding a live-service dependency.

## Residual Risks

- The current GraphML is an offline pilot snapshot for smoke and sanity testing.
  It still requires review before publication-grade claims.
- Road capacities, free-flow speeds, and disruption probabilities remain proxy
  assumptions until parameter-source tables and benchmarking are completed.
- The fallback benchmark is independent of adapted graph routing, but it is
  still an assumption-based comparator. It should be replaced or supplemented
  with cached third-party route-engine outputs before calibrated route-realism
  claims are made.
- Rail travel time, headway, and capacity remain documented assumptions for the
  pilot scaffold.
- Passing these checks means the adapted snapshot is internally plausible enough
  for scaffold testing. It does not justify operational route planning claims
  or calibrated real-world accuracy claims.
"""


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--region-path", type=Path, default=DEFAULT_REGION_PATH)
    parser.add_argument("--cache-path", type=Path, default=DEFAULT_CACHE_PATH)
    parser.add_argument("--output-path", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument(
        "--benchmark-output-path",
        type=Path,
        default=DEFAULT_BENCHMARK_OUTPUT_PATH,
    )
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
