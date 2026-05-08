"""Generate optional OSRM route benchmark comparisons for the pilot graph."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import Any, Mapping

import yaml


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld import build_simulator_graph, load_graphml
from src.realworld.plausibility import (
    BENCHMARK_CSV_FIELDS,
    DEFAULT_OSRM_BASE_URL,
    benchmark_records_to_csv_rows,
    benchmark_status_counts,
    build_osrm_route_benchmarks,
    evaluate_external_route_benchmarks,
)
from src.realworld.osrm_snapshot_manifest import (
    DEFAULT_OSRM_BENCHMARK_MANIFEST_PATH,
    DEFAULT_OSRM_RAW_RESPONSE_DIR,
    write_osrm_snapshot_manifest,
)


DEFAULT_REGION_PATH = ROOT / "data" / "regions" / "pilot_region.yaml"
DEFAULT_CACHE_PATH = ROOT / "data" / "cache" / "pilot_region_road.graphml"
DEFAULT_OUTPUT_PATH = ROOT / "data" / "validation" / "external_route_benchmarks_osrm.csv"
DEFAULT_SUMMARY_PATH = ROOT / "data" / "validation" / "osrm_route_benchmark_summary.md"
DEFAULT_MANIFEST_PATH = ROOT / "data" / "validation" / "osrm_route_benchmark_manifest.json"


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    result = run_osrm_route_benchmark(
        region_path=args.region_path,
        cache_path=args.cache_path,
        output_path=args.output_path,
        summary_path=args.summary_path,
        manifest_path=args.manifest_path,
        base_url=args.base_url,
        timeout_s=args.timeout,
        raw_output_dir=args.raw_output_dir,
    )
    print(
        "Pilot OSRM benchmark outputs written: "
        f"{result['row_count']} rows, status={result['status_counts']}"
    )
    print(f"csv: {result['output_path']}")
    print(f"summary: {result['summary_path']}")
    print(f"manifest: {result['manifest_path']}")
    return 0


def run_osrm_route_benchmark(
    *,
    region_path: str | Path = DEFAULT_REGION_PATH,
    cache_path: str | Path = DEFAULT_CACHE_PATH,
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
    summary_path: str | Path = DEFAULT_SUMMARY_PATH,
    manifest_path: str | Path = DEFAULT_MANIFEST_PATH,
    base_url: str = DEFAULT_OSRM_BASE_URL,
    timeout_s: float = 20.0,
    raw_output_dir: str | Path | None = None,
) -> dict[str, object]:
    """Call OSRM once per canonical route and store comparison rows."""

    region = _load_yaml_mapping(Path(region_path))
    road_graph = load_graphml(cache_path, normalize=True)
    simulator_graph = build_simulator_graph(road_graph, region)
    captured_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    raw_dir = Path(raw_output_dir) if raw_output_dir else None
    snapshot_reference_version = (
        _snapshot_reference_version(captured_at)
        if raw_dir is not None
        else "live_snapshot_unpinned"
    )
    source_class = (
        "cached_external_router_snapshot"
        if raw_dir is not None
        else "live_external_router_snapshot"
    )
    payload_callback = (
        _raw_payload_writer(raw_dir, captured_at, snapshot_reference_version)
        if raw_dir is not None
        else None
    )
    benchmarks = build_osrm_route_benchmarks(
        simulator_graph,
        base_url=base_url,
        timeout_s=timeout_s,
        source_class=source_class,
        reference_version=snapshot_reference_version,
        payload_callback=payload_callback,
    )
    records = evaluate_external_route_benchmarks(
        simulator_graph,
        benchmarks,
        region_id=str(region["region_id"]),
    )
    counts = benchmark_status_counts(records)

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=BENCHMARK_CSV_FIELDS)
        writer.writeheader()
        writer.writerows(benchmark_records_to_csv_rows(records))

    summary = Path(summary_path)
    summary.parent.mkdir(parents=True, exist_ok=True)
    summary.write_text(
        _summary_text(
            region_id=str(region["region_id"]),
            cache_path=Path(cache_path),
            output_path=output,
            row_count=len(records),
            counts=counts,
            records=records,
            graph_nodes=simulator_graph.number_of_nodes(),
            graph_edges=simulator_graph.number_of_edges(),
            base_url=base_url,
        ),
        encoding="utf-8",
    )
    manifest = write_osrm_snapshot_manifest(
        benchmark_path=output,
        summary_path=summary,
        manifest_path=manifest_path,
        raw_response_dir=raw_dir if raw_dir is not None else DEFAULT_OSRM_RAW_RESPONSE_DIR,
    )
    return {
        "row_count": len(records),
        "status_counts": counts,
        "output_path": str(output),
        "summary_path": str(summary),
        "manifest_path": str(manifest_path),
        "manifest_sha256": manifest["csv_sha256"],
        "raw_output_dir": "" if raw_dir is None else str(raw_dir),
    }


def _summary_text(
    *,
    region_id: str,
    cache_path: Path,
    output_path: Path,
    row_count: int,
    counts: dict[str, int],
    records,
    graph_nodes: int,
    graph_edges: int,
    base_url: str,
) -> str:
    flagged = [
        record
        for record in records
        if record.status in {"warn", "fail"}
    ]
    flagged_text = "\n".join(
        (
            f"- `{record.route_check_id}` {record.subject}: status={record.status}, "
            f"distance_ratio={record.distance_ratio:.3f}, "
            f"time_ratio={record.time_ratio:.3f}"
        )
        for record in flagged
    ) or "- No warn/fail benchmark rows in this snapshot."
    return f"""# Optional OSRM Route Benchmark Summary

Region ID: `{region_id}`

Evidence class: optional external-router plausibility evidence. This is not
ground truth and does not calibrate emergency operations.

## Inputs

- Cached road graph: `{_display_path(cache_path)}`
- OSRM base URL: `{base_url}`
- Output table: `{_display_path(output_path)}`

## Current Snapshot Results

- Adapted graph nodes: {graph_nodes}
- Adapted graph edges: {graph_edges}
- Benchmark checks: {row_count}
- Pass: {counts.get("pass", 0)}
- Warn: {counts.get("warn", 0)}
- Fail: {counts.get("fail", 0)}

The adapted graph filters pedestrian, cycling, platform, construction, track,
living-street, and service-only OSM geometries out of bus-practical simulator
routes before the OSRM comparison is built.

## Warn/Fail Rows

{flagged_text}

## Claim Boundary

The OSRM public demo service is an external routing reference for route-distance
and travel-time plausibility only. It is not a calibrated local traffic model,
not a public-agency forecast, and not an operational route plan. Keep the
offline fallback benchmark as the default deterministic validation layer.

Any warn or fail row should be treated as a reason to limit claims, inspect the
adapted graph route, or revise the accepted analysis corridor before publishing
route-realism conclusions.
"""


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--region-path", type=Path, default=DEFAULT_REGION_PATH)
    parser.add_argument("--cache-path", type=Path, default=DEFAULT_CACHE_PATH)
    parser.add_argument("--output-path", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--summary-path", type=Path, default=DEFAULT_SUMMARY_PATH)
    parser.add_argument(
        "--manifest-path",
        type=Path,
        default=DEFAULT_OSRM_BENCHMARK_MANIFEST_PATH,
    )
    parser.add_argument("--base-url", default=DEFAULT_OSRM_BASE_URL)
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument(
        "--raw-output-dir",
        type=Path,
        default=None,
        help=(
            "Optional directory for retained raw OSRM JSON responses. "
            "Supplying this improves reviewer traceability but does not "
            "create validation acceptance."
        ),
    )
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


def _snapshot_reference_version(captured_at_utc: str) -> str:
    compact = (
        captured_at_utc.replace("+00:00", "Z")
        .replace("-", "")
        .replace(":", "")
    )
    return f"cached_osrm_snapshot_{compact}"


def _raw_payload_writer(
    raw_dir: Path,
    captured_at_utc: str,
    snapshot_reference_version: str,
):
    raw_dir.mkdir(parents=True, exist_ok=True)

    def write_payload(route, url: str, payload: Mapping[str, Any]) -> None:
        target = raw_dir / f"{route.check_id}.json"
        value = {
            "schema_version": 1,
            "captured_at_utc": captured_at_utc,
            "route_check_id": route.check_id,
            "subject": f"{route.source}->{route.target}",
            "route_label": route.label,
            "query_url": url,
            "snapshot_reference_version": snapshot_reference_version,
            "claim_boundary": (
                "Raw OSRM payload retained for route-plausibility review only; "
                "not validation acceptance, not calibrated traffic evidence, "
                "and not operational routing guidance."
            ),
            "payload": payload,
        }
        target.write_text(
            json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    return write_payload


if __name__ == "__main__":
    raise SystemExit(main())
