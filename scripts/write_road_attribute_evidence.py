"""Write edge-level road-attribute evidence table and manifest."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.road_attribute_evidence import (  # noqa: E402
    DEFAULT_ROAD_ATTRIBUTE_EVIDENCE_MANIFEST_PATH,
    DEFAULT_ROAD_ATTRIBUTE_EVIDENCE_PATH,
    build_cached_road_attribute_evidence_rows,
    write_road_attribute_evidence,
)
from src.realworld.road_capacity_evidence import DEFAULT_CAPACITY_PER_LANE_VPH  # noqa: E402
from src.realworld.road_evidence import DEFAULT_ROAD_GRAPH_PATH  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    benchmark_times = _load_benchmark_times(
        args.benchmark_times_csv,
        edge_id_column=args.benchmark_edge_id_column,
        travel_time_column=args.benchmark_travel_time_column,
    )
    if benchmark_times and (
        not args.benchmark_source_label or not args.benchmark_snapshot_path
    ):
        raise SystemExit(
            "Benchmark times require --benchmark-source-label and "
            "--benchmark-snapshot-path so benchmark evidence is traceable."
        )
    rows = build_cached_road_attribute_evidence_rows(
        args.input_graph,
        benchmark_travel_time_by_edge_id=benchmark_times,
        benchmark_source_label=args.benchmark_source_label,
        benchmark_snapshot_path=args.benchmark_snapshot_path,
        capacity_per_lane_vph=args.capacity_per_lane_vph,
    )
    manifest = write_road_attribute_evidence(
        rows=rows,
        output_path=args.output,
        manifest_path=args.manifest,
        source_graph_path=args.input_graph,
        benchmark_source_label=args.benchmark_source_label,
        benchmark_snapshot_path=args.benchmark_snapshot_path,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write edge-level road-attribute evidence. The output is a "
            "non-acceptance review aid, not a calibrated road override table."
        )
    )
    parser.add_argument(
        "--input-graph",
        type=Path,
        default=DEFAULT_ROAD_GRAPH_PATH,
        help="Cached OSM/GraphML graph path.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_ROAD_ATTRIBUTE_EVIDENCE_PATH,
        help="Road-attribute evidence CSV path.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_ROAD_ATTRIBUTE_EVIDENCE_MANIFEST_PATH,
        help="Manifest JSON path.",
    )
    parser.add_argument(
        "--capacity-per-lane-vph",
        type=float,
        default=DEFAULT_CAPACITY_PER_LANE_VPH,
        help="Planning proxy used only for lane-based capacity candidates.",
    )
    parser.add_argument(
        "--benchmark-times-csv",
        type=Path,
        default=None,
        help="Optional CSV with benchmark travel times keyed by edge ID.",
    )
    parser.add_argument(
        "--benchmark-edge-id-column",
        default="edge_id",
        help="Benchmark CSV edge ID column.",
    )
    parser.add_argument(
        "--benchmark-travel-time-column",
        default="benchmark_travel_time_min",
        help="Benchmark CSV positive travel-time column in minutes.",
    )
    parser.add_argument(
        "--benchmark-source-label",
        default="",
        help="Required when benchmark times are supplied.",
    )
    parser.add_argument(
        "--benchmark-snapshot-path",
        type=Path,
        default=None,
        help="Required cached benchmark snapshot path when benchmark times are supplied.",
    )
    return parser.parse_args(argv)


def _load_benchmark_times(
    path: Path | None,
    *,
    edge_id_column: str,
    travel_time_column: str,
) -> dict[str, float]:
    if path is None:
        return {}
    values: dict[str, float] = {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if edge_id_column not in (reader.fieldnames or ()):
            raise ValueError(f"{path} missing benchmark edge ID column {edge_id_column!r}")
        if travel_time_column not in (reader.fieldnames or ()):
            raise ValueError(
                f"{path} missing benchmark travel-time column {travel_time_column!r}"
            )
        for row in reader:
            edge_id = str(row.get(edge_id_column, "")).strip()
            if not edge_id:
                continue
            values[edge_id] = float(row[travel_time_column])
    return values


if __name__ == "__main__":
    raise SystemExit(main())
