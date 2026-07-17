"""Write the metric-level Morris index review packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.sensitivity import (  # noqa: E402
    DEFAULT_MORRIS_MANIFEST_PATH,
    DEFAULT_MORRIS_SUMMARY_PATH,
)
from src.realworld.sensitivity_index_review_packet import (  # noqa: E402
    DEFAULT_SENSITIVITY_INDEX_REVIEW_DOC_PATH,
    DEFAULT_SENSITIVITY_INDEX_REVIEW_MANIFEST_PATH,
    DEFAULT_SENSITIVITY_INDEX_REVIEW_PACKET_PATH,
    build_sensitivity_index_review_rows,
    write_sensitivity_index_review_packet,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    rows = build_sensitivity_index_review_rows(
        summary_path=args.summary,
        manifest_path=args.morris_manifest,
    )
    manifest = write_sensitivity_index_review_packet(
        rows=rows,
        output_path=args.output,
        manifest_path=args.manifest,
        doc_path=args.doc,
        summary_path=args.summary,
        morris_manifest_path=args.morris_manifest,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write a conservative metric-level Morris index review packet. "
            "The output is review support only, not sensitivity acceptance."
        )
    )
    parser.add_argument("--summary", type=Path, default=DEFAULT_MORRIS_SUMMARY_PATH)
    parser.add_argument(
        "--morris-manifest",
        type=Path,
        default=DEFAULT_MORRIS_MANIFEST_PATH,
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_SENSITIVITY_INDEX_REVIEW_PACKET_PATH,
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_SENSITIVITY_INDEX_REVIEW_MANIFEST_PATH,
    )
    parser.add_argument(
        "--doc",
        type=Path,
        default=DEFAULT_SENSITIVITY_INDEX_REVIEW_DOC_PATH,
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
