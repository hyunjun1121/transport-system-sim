"""Write cached OSM maxspeed candidate evidence by road class."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.road_evidence import DEFAULT_ROAD_GRAPH_PATH  # noqa: E402
from src.realworld.road_speed_evidence import (  # noqa: E402
    DEFAULT_ROAD_SPEED_EVIDENCE_MANIFEST_PATH,
    DEFAULT_ROAD_SPEED_EVIDENCE_PATH,
    build_cached_road_speed_evidence_rows,
    write_road_speed_evidence,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    rows = build_cached_road_speed_evidence_rows(args.input_graph)
    manifest = write_road_speed_evidence(
        rows=rows,
        output_path=args.output,
        manifest_path=args.manifest,
        source_graph_path=args.input_graph,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Summarize sparse cached OSM maxspeed tags by routeable road class. "
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
        default=DEFAULT_ROAD_SPEED_EVIDENCE_PATH,
        help="Candidate speed evidence CSV path.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_ROAD_SPEED_EVIDENCE_MANIFEST_PATH,
        help="Manifest JSON path.",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
