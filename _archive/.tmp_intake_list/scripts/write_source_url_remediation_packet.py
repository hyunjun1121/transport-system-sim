"""Write the current source-URL remediation packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.source_url_remediation_packet import (  # noqa: E402
    DEFAULT_SOURCE_URL_REMEDIATION_DOC_PATH,
    DEFAULT_SOURCE_URL_REMEDIATION_MANIFEST_PATH,
    DEFAULT_SOURCE_URL_REMEDIATION_PACKET_PATH,
    build_source_url_remediation_rows,
    write_source_url_remediation_packet,
)
from src.realworld.source_url_review_packet import (  # noqa: E402
    DEFAULT_SOURCE_URL_REVIEW_PACKET_PATH,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    rows = build_source_url_remediation_rows(
        url_review_packet_path=args.source_url_review_packet,
    )
    manifest = write_source_url_remediation_packet(
        rows=rows,
        output_path=args.output,
        manifest_path=args.manifest,
        doc_path=args.doc,
        url_review_packet_path=args.source_url_review_packet,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write source-URL remediation rows from the current URL review packet. "
            "The output is a reviewer packet and does not create provenance acceptance."
        )
    )
    parser.add_argument(
        "--source-url-review-packet",
        type=Path,
        default=DEFAULT_SOURCE_URL_REVIEW_PACKET_PATH,
        help="Source URL review CSV path.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_SOURCE_URL_REMEDIATION_PACKET_PATH,
        help="Source URL remediation CSV path.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_SOURCE_URL_REMEDIATION_MANIFEST_PATH,
        help="Source URL remediation manifest JSON path.",
    )
    parser.add_argument(
        "--doc",
        type=Path,
        default=DEFAULT_SOURCE_URL_REMEDIATION_DOC_PATH,
        help="Source URL remediation Markdown path.",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
