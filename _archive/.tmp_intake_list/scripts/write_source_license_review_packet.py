"""Write the current source/license review packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.source_license_review_packet import (  # noqa: E402
    DEFAULT_SOURCE_LICENSE_REVIEW_DOC_PATH,
    DEFAULT_SOURCE_LICENSE_REVIEW_MANIFEST_PATH,
    DEFAULT_SOURCE_LICENSE_REVIEW_PACKET_PATH,
    build_source_license_review_rows,
    write_source_license_review_packet,
)
from src.realworld.source_provenance import DEFAULT_SOURCE_PROVENANCE_PATH  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    rows = build_source_license_review_rows(
        provenance_manifest_path=args.source_provenance_manifest,
    )
    manifest = write_source_license_review_packet(
        rows=rows,
        output_path=args.output,
        manifest_path=args.manifest,
        doc_path=args.doc,
        provenance_manifest_path=args.source_provenance_manifest,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write source/license review rows. The output is a reviewer packet "
            "and does not create provenance acceptance."
        )
    )
    parser.add_argument(
        "--source-provenance-manifest",
        type=Path,
        default=DEFAULT_SOURCE_PROVENANCE_PATH,
        help="Source provenance manifest JSON path.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_SOURCE_LICENSE_REVIEW_PACKET_PATH,
        help="Source/license review CSV path.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_SOURCE_LICENSE_REVIEW_MANIFEST_PATH,
        help="Source/license review manifest JSON path.",
    )
    parser.add_argument(
        "--doc",
        type=Path,
        default=DEFAULT_SOURCE_LICENSE_REVIEW_DOC_PATH,
        help="Source/license review Markdown path.",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
