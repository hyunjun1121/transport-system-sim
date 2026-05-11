"""Write the rail evidence priority packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.rail_evidence_priority_packet import (  # noqa: E402
    DEFAULT_RAIL_EVIDENCE_PRIORITY_DOC_PATH,
    DEFAULT_RAIL_EVIDENCE_PRIORITY_MANIFEST_PATH,
    DEFAULT_RAIL_EVIDENCE_PRIORITY_PACKET_PATH,
    build_rail_evidence_priority_rows,
    write_rail_evidence_priority_packet,
)
from src.realworld.rail_evidence_review_packet import (  # noqa: E402
    DEFAULT_RAIL_EVIDENCE_REVIEW_PACKET_PATH,
)
from src.realworld.rail_fetch_readiness_packet import (  # noqa: E402
    DEFAULT_RAIL_FETCH_READINESS_PACKET_PATH,
)
from src.realworld.rail_timing_request_packet import (  # noqa: E402
    DEFAULT_RAIL_TIMING_SOURCE_REQUEST_PACKET_PATH,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    rows = build_rail_evidence_priority_rows(
        evidence_review_path=args.evidence_review,
        timing_request_path=args.timing_request,
        fetch_readiness_path=args.fetch_readiness,
    )
    manifest = write_rail_evidence_priority_packet(
        rows=rows,
        output_path=args.output,
        manifest_path=args.manifest,
        doc_path=args.doc,
        evidence_review_path=args.evidence_review,
        timing_request_path=args.timing_request,
        fetch_readiness_path=args.fetch_readiness,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write a rail evidence priority packet. The output is review "
            "support only, not rail-service evidence or acceptance."
        )
    )
    parser.add_argument(
        "--evidence-review",
        type=Path,
        default=DEFAULT_RAIL_EVIDENCE_REVIEW_PACKET_PATH,
    )
    parser.add_argument(
        "--timing-request",
        type=Path,
        default=DEFAULT_RAIL_TIMING_SOURCE_REQUEST_PACKET_PATH,
    )
    parser.add_argument(
        "--fetch-readiness",
        type=Path,
        default=DEFAULT_RAIL_FETCH_READINESS_PACKET_PATH,
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_RAIL_EVIDENCE_PRIORITY_PACKET_PATH,
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_RAIL_EVIDENCE_PRIORITY_MANIFEST_PATH,
    )
    parser.add_argument(
        "--doc",
        type=Path,
        default=DEFAULT_RAIL_EVIDENCE_PRIORITY_DOC_PATH,
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
