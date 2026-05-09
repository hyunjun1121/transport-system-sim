"""Write the road evidence priority packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.road_evidence_priority_packet import (  # noqa: E402
    DEFAULT_ROAD_EVIDENCE_PRIORITY_DOC_PATH,
    DEFAULT_ROAD_EVIDENCE_PRIORITY_MANIFEST_PATH,
    DEFAULT_ROAD_EVIDENCE_PRIORITY_PACKET_PATH,
    build_road_evidence_priority_rows,
    write_road_evidence_priority_packet,
)
from src.realworld.road_evidence_review_packet import (  # noqa: E402
    DEFAULT_ROAD_EVIDENCE_REVIEW_PACKET_PATH,
)
from src.realworld.road_source_readiness_packet import (  # noqa: E402
    DEFAULT_ROAD_SOURCE_READINESS_PACKET_PATH,
)
from src.realworld.route_road_evidence_exposure import (  # noqa: E402
    DEFAULT_ROUTE_ROAD_EVIDENCE_EXPOSURE_MANIFEST_PATH,
    DEFAULT_ROUTE_ROAD_EVIDENCE_EXPOSURE_PATH,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    rows = build_road_evidence_priority_rows(
        road_evidence_review_path=args.road_evidence_review,
        route_exposure_path=args.route_exposure,
        route_exposure_manifest_path=args.route_exposure_manifest,
        road_source_readiness_path=args.road_source_readiness,
    )
    manifest = write_road_evidence_priority_packet(
        rows=rows,
        output_path=args.output,
        manifest_path=args.manifest,
        doc_path=args.doc,
        road_evidence_review_path=args.road_evidence_review,
        route_exposure_path=args.route_exposure,
        route_exposure_manifest_path=args.route_exposure_manifest,
        road_source_readiness_path=args.road_source_readiness,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write a route-exposure-weighted road evidence priority packet. "
            "The output is review support only, not road acceptance."
        )
    )
    parser.add_argument(
        "--road-evidence-review",
        type=Path,
        default=DEFAULT_ROAD_EVIDENCE_REVIEW_PACKET_PATH,
    )
    parser.add_argument(
        "--route-exposure",
        type=Path,
        default=DEFAULT_ROUTE_ROAD_EVIDENCE_EXPOSURE_PATH,
    )
    parser.add_argument(
        "--route-exposure-manifest",
        type=Path,
        default=DEFAULT_ROUTE_ROAD_EVIDENCE_EXPOSURE_MANIFEST_PATH,
    )
    parser.add_argument(
        "--road-source-readiness",
        type=Path,
        default=DEFAULT_ROAD_SOURCE_READINESS_PACKET_PATH,
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_ROAD_EVIDENCE_PRIORITY_PACKET_PATH,
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_ROAD_EVIDENCE_PRIORITY_MANIFEST_PATH,
    )
    parser.add_argument(
        "--doc",
        type=Path,
        default=DEFAULT_ROAD_EVIDENCE_PRIORITY_DOC_PATH,
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
