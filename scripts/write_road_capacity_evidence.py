"""Write cached OSM lane-count capacity candidate evidence by road class."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.road_capacity_evidence import (  # noqa: E402
    DEFAULT_CAPACITY_PER_LANE_VPH,
    DEFAULT_ROAD_CAPACITY_EVIDENCE_MANIFEST_PATH,
    DEFAULT_ROAD_CAPACITY_EVIDENCE_PATH,
    build_cached_road_capacity_evidence_rows,
    write_road_capacity_evidence,
)
from src.realworld.road_evidence import DEFAULT_ROAD_GRAPH_PATH  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    rows = build_cached_road_capacity_evidence_rows(
        args.input_graph,
        capacity_per_lane_vph=args.capacity_per_lane_vph,
    )
    manifest = write_road_capacity_evidence(
        rows=rows,
        output_path=args.output,
        manifest_path=args.manifest,
        source_graph_path=args.input_graph,
        capacity_per_lane_vph=args.capacity_per_lane_vph,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Summarize sparse cached OSM lanes tags by routeable road class. "
            "The output is candidate evidence only, not a reviewed override table."
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
        default=DEFAULT_ROAD_CAPACITY_EVIDENCE_PATH,
        help="Candidate capacity evidence CSV path.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_ROAD_CAPACITY_EVIDENCE_MANIFEST_PATH,
        help="Manifest JSON path.",
    )
    parser.add_argument(
        "--capacity-per-lane-vph",
        type=float,
        default=DEFAULT_CAPACITY_PER_LANE_VPH,
        help="Planning proxy used to translate lane counts into candidate capacity.",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
