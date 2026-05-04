"""Write the current graph-scale method review packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.graph_scale_review import (  # noqa: E402
    DEFAULT_GRAPH_SCALE_REVIEW_MANIFEST_PATH,
    DEFAULT_GRAPH_SCALE_REVIEW_PACKET_PATH,
    build_graph_scale_review_rows,
    write_graph_scale_review_packet,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    rows = build_graph_scale_review_rows(
        route_comparison_path=args.route_comparison,
        alternate_route_path=args.alternate_routes,
        multi_corridor_route_path=args.multi_corridor_routes,
        pilot_full_manifest_path=args.pilot_full_manifest,
        multi_corridor_manifest_path=args.multi_corridor_manifest,
        multi_corridor_full_manifest_path=args.multi_corridor_full_manifest,
    )
    manifest = write_graph_scale_review_packet(
        rows=rows,
        output_path=args.output,
        manifest_path=args.manifest,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write a conservative graph-scale method review packet. The output "
            "is a review aid only, not graph-scale acceptance."
        )
    )
    parser.add_argument(
        "--route-comparison",
        type=Path,
        default=ROOT / "data" / "validation" / "graph_scale_route_comparison.csv",
    )
    parser.add_argument(
        "--alternate-routes",
        type=Path,
        default=ROOT / "data" / "validation" / "graph_scale_alternate_routes.csv",
    )
    parser.add_argument(
        "--multi-corridor-routes",
        type=Path,
        default=ROOT
        / "data"
        / "validation"
        / "graph_scale_multi_corridor_routes.csv",
    )
    parser.add_argument(
        "--pilot-full-manifest",
        type=Path,
        default=ROOT / "results" / "realworld_pilot" / "pilot_full_manifest.json",
    )
    parser.add_argument(
        "--multi-corridor-manifest",
        type=Path,
        default=ROOT
        / "results"
        / "realworld_pilot"
        / "pilot_multi_corridor_manifest.json",
    )
    parser.add_argument(
        "--multi-corridor-full-manifest",
        type=Path,
        default=ROOT
        / "results"
        / "realworld_pilot"
        / "pilot_multi_corridor_full_manifest.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_GRAPH_SCALE_REVIEW_PACKET_PATH,
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_GRAPH_SCALE_REVIEW_MANIFEST_PATH,
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
