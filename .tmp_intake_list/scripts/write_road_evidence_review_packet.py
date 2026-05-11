"""Write the current road-input evidence review packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.road_evidence import DEFAULT_ROAD_GRAPH_PATH  # noqa: E402
from src.realworld.road_evidence_review_packet import (  # noqa: E402
    DEFAULT_ROAD_EVIDENCE_REVIEW_MANIFEST_PATH,
    DEFAULT_ROAD_EVIDENCE_REVIEW_PACKET_PATH,
    build_road_evidence_review_rows,
    write_road_evidence_review_packet,
)
from src.realworld.road_override_audit import (  # noqa: E402
    DEFAULT_ROAD_CLASS_OVERRIDE_DRAFT_PATH,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    rows = build_road_evidence_review_rows(
        input_graph=args.input_graph,
        draft_override_path=args.draft_override,
    )
    manifest = write_road_evidence_review_packet(
        rows=rows,
        output_path=args.output,
        manifest_path=args.manifest,
        input_graph=args.input_graph,
        draft_override_path=args.draft_override,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write a conservative road-input evidence review packet. The output "
            "is a review aid only, not road calibration or road-class acceptance."
        )
    )
    parser.add_argument(
        "--input-graph",
        type=Path,
        default=DEFAULT_ROAD_GRAPH_PATH,
        help="Cached OSM/GraphML graph path.",
    )
    parser.add_argument(
        "--draft-override",
        type=Path,
        default=DEFAULT_ROAD_CLASS_OVERRIDE_DRAFT_PATH,
        help="Draft road-class override worksheet path.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_ROAD_EVIDENCE_REVIEW_PACKET_PATH,
        help="Road evidence review CSV path.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_ROAD_EVIDENCE_REVIEW_MANIFEST_PATH,
        help="Road evidence review manifest JSON path.",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
