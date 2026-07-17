"""Write the rail source decision packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.rail_evidence_priority_packet import (  # noqa: E402
    DEFAULT_RAIL_EVIDENCE_PRIORITY_MANIFEST_PATH,
    DEFAULT_RAIL_EVIDENCE_PRIORITY_PACKET_PATH,
)
from src.realworld.rail_evidence_review_packet import (  # noqa: E402
    DEFAULT_RAIL_EVIDENCE_REVIEW_PACKET_PATH,
)
from src.realworld.rail_fetch_readiness_packet import (  # noqa: E402
    DEFAULT_RAIL_FETCH_READINESS_MANIFEST_PATH,
    DEFAULT_RAIL_FETCH_READINESS_PACKET_PATH,
)
from src.realworld.rail_source_decision_packet import (  # noqa: E402
    DEFAULT_RAIL_SOURCE_DECISION_DOC_PATH,
    DEFAULT_RAIL_SOURCE_DECISION_MANIFEST_PATH,
    DEFAULT_RAIL_SOURCE_DECISION_PACKET_PATH,
    build_rail_source_decision_rows,
    write_rail_source_decision_packet,
)
from src.realworld.rail_timing_request_packet import (  # noqa: E402
    DEFAULT_RAIL_TIMING_SOURCE_REQUEST_PACKET_PATH,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    rows = build_rail_source_decision_rows(
        fetch_readiness_path=args.fetch_readiness_packet,
        fetch_readiness_manifest_path=args.fetch_readiness_manifest,
        priority_packet_path=args.priority_packet,
        priority_manifest_path=args.priority_manifest,
        timing_request_packet_path=args.timing_request_packet,
        rail_review_packet_path=args.rail_review_packet,
    )
    manifest = write_rail_source_decision_packet(
        rows=rows,
        output_path=args.output,
        manifest_path=args.manifest,
        doc_path=args.doc,
        fetch_readiness_path=args.fetch_readiness_packet,
        fetch_readiness_manifest_path=args.fetch_readiness_manifest,
        priority_packet_path=args.priority_packet,
        priority_manifest_path=args.priority_manifest,
        timing_request_packet_path=args.timing_request_packet,
        rail_review_packet_path=args.rail_review_packet,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write a rail source-decision packet. The output is review support "
            "only, not rail timing evidence, GTFS validation, or rail evidence "
            "acceptance."
        )
    )
    parser.add_argument(
        "--fetch-readiness-packet",
        type=Path,
        default=DEFAULT_RAIL_FETCH_READINESS_PACKET_PATH,
    )
    parser.add_argument(
        "--fetch-readiness-manifest",
        type=Path,
        default=DEFAULT_RAIL_FETCH_READINESS_MANIFEST_PATH,
    )
    parser.add_argument(
        "--priority-packet",
        type=Path,
        default=DEFAULT_RAIL_EVIDENCE_PRIORITY_PACKET_PATH,
    )
    parser.add_argument(
        "--priority-manifest",
        type=Path,
        default=DEFAULT_RAIL_EVIDENCE_PRIORITY_MANIFEST_PATH,
    )
    parser.add_argument(
        "--timing-request-packet",
        type=Path,
        default=DEFAULT_RAIL_TIMING_SOURCE_REQUEST_PACKET_PATH,
    )
    parser.add_argument(
        "--rail-review-packet",
        type=Path,
        default=DEFAULT_RAIL_EVIDENCE_REVIEW_PACKET_PATH,
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_RAIL_SOURCE_DECISION_PACKET_PATH,
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_RAIL_SOURCE_DECISION_MANIFEST_PATH,
    )
    parser.add_argument(
        "--doc",
        type=Path,
        default=DEFAULT_RAIL_SOURCE_DECISION_DOC_PATH,
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
