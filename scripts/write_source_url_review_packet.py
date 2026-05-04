"""Write the current source URL review packet.

By default this command only parses URLs from source provenance records. Use
``--live`` to record best-effort HTTP reachability. Neither mode creates source
or provenance acceptance.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.source_provenance import DEFAULT_SOURCE_PROVENANCE_PATH  # noqa: E402
from src.realworld.source_url_review_packet import (  # noqa: E402
    DEFAULT_SOURCE_URL_REVIEW_DOC_PATH,
    DEFAULT_SOURCE_URL_REVIEW_MANIFEST_PATH,
    DEFAULT_SOURCE_URL_REVIEW_PACKET_PATH,
    build_source_url_review_rows,
    write_source_url_review_packet,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    rows = build_source_url_review_rows(
        provenance_manifest_path=args.source_provenance_manifest,
        live_check=args.live,
        timeout_sec=args.timeout_sec,
    )
    manifest = write_source_url_review_packet(
        rows=rows,
        output_path=args.output,
        manifest_path=args.manifest,
        doc_path=args.doc,
        provenance_manifest_path=args.source_provenance_manifest,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-provenance-manifest",
        type=Path,
        default=DEFAULT_SOURCE_PROVENANCE_PATH,
        help="Source provenance manifest JSON path.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_SOURCE_URL_REVIEW_PACKET_PATH,
        help="Source URL review CSV path.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_SOURCE_URL_REVIEW_MANIFEST_PATH,
        help="Source URL review manifest JSON path.",
    )
    parser.add_argument(
        "--doc",
        type=Path,
        default=DEFAULT_SOURCE_URL_REVIEW_DOC_PATH,
        help="Source URL review Markdown path.",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Perform bounded live HTTP reachability checks.",
    )
    parser.add_argument(
        "--timeout-sec",
        type=float,
        default=8.0,
        help="Per-URL timeout for --live checks.",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
