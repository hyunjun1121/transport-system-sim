"""Write the parameter evidence priority packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.parameter_evidence_priority_packet import (  # noqa: E402
    DEFAULT_PARAMETER_EVIDENCE_PRIORITY_DOC_PATH,
    DEFAULT_PARAMETER_EVIDENCE_PRIORITY_MANIFEST_PATH,
    DEFAULT_PARAMETER_EVIDENCE_PRIORITY_PACKET_PATH,
    build_parameter_evidence_priority_rows,
    write_parameter_evidence_priority_packet,
)
from src.realworld.parameter_evidence_request_packet import (  # noqa: E402
    DEFAULT_PARAMETER_EVIDENCE_SOURCE_REQUEST_PACKET_PATH,
)
from src.realworld.parameter_review_packet import (  # noqa: E402
    DEFAULT_PARAMETER_REVIEW_PACKET_PATH,
)
from src.realworld.parameter_source_readiness_packet import (  # noqa: E402
    DEFAULT_PARAMETER_SOURCE_READINESS_PACKET_PATH,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    rows = build_parameter_evidence_priority_rows(
        review_packet_path=args.review_packet,
        source_request_path=args.source_request,
        source_readiness_path=args.source_readiness,
    )
    manifest = write_parameter_evidence_priority_packet(
        rows=rows,
        output_path=args.output,
        manifest_path=args.manifest,
        doc_path=args.doc,
        review_packet_path=args.review_packet,
        source_request_path=args.source_request,
        source_readiness_path=args.source_readiness,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write a parameter evidence priority packet. The output is review "
            "support only, not accepted parameter evidence or calibration."
        )
    )
    parser.add_argument(
        "--review-packet",
        type=Path,
        default=DEFAULT_PARAMETER_REVIEW_PACKET_PATH,
    )
    parser.add_argument(
        "--source-request",
        type=Path,
        default=DEFAULT_PARAMETER_EVIDENCE_SOURCE_REQUEST_PACKET_PATH,
    )
    parser.add_argument(
        "--source-readiness",
        type=Path,
        default=DEFAULT_PARAMETER_SOURCE_READINESS_PACKET_PATH,
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_PARAMETER_EVIDENCE_PRIORITY_PACKET_PATH,
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_PARAMETER_EVIDENCE_PRIORITY_MANIFEST_PATH,
    )
    parser.add_argument(
        "--doc",
        type=Path,
        default=DEFAULT_PARAMETER_EVIDENCE_PRIORITY_DOC_PATH,
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
