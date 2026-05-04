"""Write the current manuscript/report claim-alignment review packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.claim_alignment_review_packet import (  # noqa: E402
    DEFAULT_CLAIM_ALIGNMENT_REVIEW_DOC_PATH,
    DEFAULT_CLAIM_ALIGNMENT_REVIEW_MANIFEST_PATH,
    DEFAULT_CLAIM_ALIGNMENT_REVIEW_PACKET_PATH,
    DEFAULT_FIGURE_TABLE_MANIFEST_PATH,
    DEFAULT_PAPER_DRAFT_PATH,
    DEFAULT_REPORT_DRAFT_PATH,
    build_claim_alignment_review_rows,
    write_claim_alignment_review_packet,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    rows = build_claim_alignment_review_rows(
        paper_path=args.paper,
        report_path=args.report,
        figure_manifest_path=args.figure_manifest,
    )
    manifest = write_claim_alignment_review_packet(
        rows=rows,
        output_path=args.output,
        manifest_path=args.manifest,
        doc_path=args.doc,
        paper_path=args.paper,
        report_path=args.report,
        figure_manifest_path=args.figure_manifest,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write claim-alignment review rows. The output is a reviewer packet "
            "and does not create manuscript acceptance."
        )
    )
    parser.add_argument("--paper", type=Path, default=DEFAULT_PAPER_DRAFT_PATH)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT_DRAFT_PATH)
    parser.add_argument(
        "--figure-manifest",
        type=Path,
        default=DEFAULT_FIGURE_TABLE_MANIFEST_PATH,
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_CLAIM_ALIGNMENT_REVIEW_PACKET_PATH,
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_CLAIM_ALIGNMENT_REVIEW_MANIFEST_PATH,
    )
    parser.add_argument(
        "--doc",
        type=Path,
        default=DEFAULT_CLAIM_ALIGNMENT_REVIEW_DOC_PATH,
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
