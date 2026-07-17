"""Write canonical route road-evidence exposure artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.pilot_experiments import (  # noqa: E402
    DEFAULT_CACHE_PATH,
    DEFAULT_REGION_PATH,
    load_pilot_inputs,
)
from src.realworld.route_road_evidence_exposure import (  # noqa: E402
    DEFAULT_CURRENT_ALTERNATE_ROUTES_PATH,
    DEFAULT_MULTI_CORRIDOR_ROUTES_PATH,
    DEFAULT_ROUTE_ROAD_EVIDENCE_EXPOSURE_MANIFEST_PATH,
    DEFAULT_ROUTE_ROAD_EVIDENCE_EXPOSURE_PATH,
    DEFAULT_ROUTE_ROAD_EVIDENCE_EXPOSURE_SUMMARY_PATH,
    build_route_road_evidence_exposure_rows,
    write_route_road_evidence_exposure,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    inputs = load_pilot_inputs(
        region_path=args.region_path,
        cache_path=args.cache_path,
        reduce_graph=False,
    )
    graph_variant_paths = (
        ("current_reduced_corridor", args.current_alternate_routes),
        ("multi_corridor_candidate", args.multi_corridor_routes),
    )
    rows = build_route_road_evidence_exposure_rows(
        inputs.graph,
        road_evidence_review_path=args.road_evidence_review,
        graph_variant_paths=graph_variant_paths,
    )
    manifest = write_route_road_evidence_exposure(
        rows=rows,
        output_path=args.output,
        summary_path=args.summary,
        manifest_path=args.manifest,
        road_evidence_review_path=args.road_evidence_review,
        graph_variant_paths=graph_variant_paths,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write route-level road-evidence exposure rows. The artifacts are "
            "review support only, not calibration or acceptance."
        )
    )
    parser.add_argument("--region-path", type=Path, default=DEFAULT_REGION_PATH)
    parser.add_argument("--cache-path", type=Path, default=DEFAULT_CACHE_PATH)
    parser.add_argument(
        "--road-evidence-review",
        type=Path,
        default=ROOT / "data" / "parameters" / "road_evidence_review_packet.csv",
    )
    parser.add_argument(
        "--current-alternate-routes",
        type=Path,
        default=DEFAULT_CURRENT_ALTERNATE_ROUTES_PATH,
    )
    parser.add_argument(
        "--multi-corridor-routes",
        type=Path,
        default=DEFAULT_MULTI_CORRIDOR_ROUTES_PATH,
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_ROUTE_ROAD_EVIDENCE_EXPOSURE_PATH,
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=DEFAULT_ROUTE_ROAD_EVIDENCE_EXPOSURE_SUMMARY_PATH,
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_ROUTE_ROAD_EVIDENCE_EXPOSURE_MANIFEST_PATH,
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
