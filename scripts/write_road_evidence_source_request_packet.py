"""Write the current road evidence source-request packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.road_evidence_request_packet import (  # noqa: E402
    DEFAULT_ROAD_EVIDENCE_SOURCE_REQUEST_MANIFEST_PATH,
    DEFAULT_ROAD_EVIDENCE_SOURCE_REQUEST_PACKET_PATH,
    build_road_evidence_source_request_rows,
    write_road_evidence_source_request_packet,
)
from src.realworld.road_evidence_review_packet import (  # noqa: E402
    DEFAULT_ROAD_EVIDENCE_REVIEW_PACKET_PATH,
)
from src.realworld.road_override_audit import (  # noqa: E402
    DEFAULT_ROAD_CLASS_OVERRIDE_DRAFT_PATH,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    rows = build_road_evidence_source_request_rows(
        review_packet_path=args.review_packet,
        draft_override_path=args.draft_overrides,
    )
    manifest = write_road_evidence_source_request_packet(
        rows=rows,
        output_path=args.output,
        manifest_path=args.manifest,
        review_packet_path=args.review_packet,
        draft_override_path=args.draft_overrides,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write the road evidence source-request worksheet. The output names "
            "required source inputs and review commands; it is not road evidence."
        )
    )
    parser.add_argument(
        "--review-packet",
        type=Path,
        default=DEFAULT_ROAD_EVIDENCE_REVIEW_PACKET_PATH,
        help="Road evidence review packet CSV path.",
    )
    parser.add_argument(
        "--draft-overrides",
        type=Path,
        default=DEFAULT_ROAD_CLASS_OVERRIDE_DRAFT_PATH,
        help="Draft road-class override CSV path.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_ROAD_EVIDENCE_SOURCE_REQUEST_PACKET_PATH,
        help="Road evidence source-request CSV path.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_ROAD_EVIDENCE_SOURCE_REQUEST_MANIFEST_PATH,
        help="Road evidence source-request manifest JSON path.",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
