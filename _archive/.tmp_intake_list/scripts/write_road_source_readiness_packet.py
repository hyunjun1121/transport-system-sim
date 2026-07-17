"""Write the current road source-readiness packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.road_evidence_request_packet import (  # noqa: E402
    DEFAULT_ROAD_EVIDENCE_SOURCE_REQUEST_PACKET_PATH,
)
from src.realworld.road_source_readiness_packet import (  # noqa: E402
    DEFAULT_ROAD_SOURCE_READINESS_DOC_PATH,
    DEFAULT_ROAD_SOURCE_READINESS_MANIFEST_PATH,
    DEFAULT_ROAD_SOURCE_READINESS_PACKET_PATH,
    build_road_source_readiness_rows,
    write_road_source_readiness_packet,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    rows = build_road_source_readiness_rows(
        request_packet_path=args.request_packet,
    )
    manifest = write_road_source_readiness_packet(
        rows=rows,
        output_path=args.output,
        manifest_path=args.manifest,
        doc_path=args.doc,
        request_packet_path=args.request_packet,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write road source-readiness rows from the current road evidence "
            "source-request packet. The output is a reviewer packet and does "
            "not create road-class override evidence."
        )
    )
    parser.add_argument(
        "--request-packet",
        type=Path,
        default=DEFAULT_ROAD_EVIDENCE_SOURCE_REQUEST_PACKET_PATH,
        help="Road evidence source-request CSV path.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_ROAD_SOURCE_READINESS_PACKET_PATH,
        help="Road source-readiness CSV path.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_ROAD_SOURCE_READINESS_MANIFEST_PATH,
        help="Road source-readiness manifest JSON path.",
    )
    parser.add_argument(
        "--doc",
        type=Path,
        default=DEFAULT_ROAD_SOURCE_READINESS_DOC_PATH,
        help="Road source-readiness Markdown path.",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
