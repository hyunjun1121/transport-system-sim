"""Write the manuscript/report decision packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.claim_alignment_review_packet import (  # noqa: E402
    DEFAULT_CLAIM_ALIGNMENT_REVIEW_MANIFEST_PATH,
)
from src.realworld.figure_table_review_packet import (  # noqa: E402
    DEFAULT_FIGURE_TABLE_REVIEW_MANIFEST_PATH,
)
from src.realworld.manuscript_acceptance import (  # noqa: E402
    DEFAULT_MANUSCRIPT_ACCEPTANCE_PATH,
)
from src.realworld.manuscript_report_decision_packet import (  # noqa: E402
    DEFAULT_FIGURE_TABLE_MANIFEST_PATH,
    DEFAULT_MANUSCRIPT_REPORT_DECISION_DOC_PATH,
    DEFAULT_MANUSCRIPT_REPORT_DECISION_MANIFEST_PATH,
    DEFAULT_MANUSCRIPT_REPORT_DECISION_PACKET_PATH,
    DEFAULT_PAPER_DRAFT_PATH,
    DEFAULT_REPORT_DOCX_PATH,
    DEFAULT_REPORT_DRAFT_PATH,
    build_manuscript_report_decision_rows,
    write_manuscript_report_decision_packet,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    rows = build_manuscript_report_decision_rows(
        paper_path=args.paper,
        report_path=args.report,
        report_docx_path=args.report_docx,
        figure_manifest_path=args.figure_manifest,
        claim_alignment_manifest_path=args.claim_alignment_manifest,
        figure_table_review_manifest_path=args.figure_table_review_manifest,
        manuscript_acceptance_path=args.manuscript_acceptance,
    )
    manifest = write_manuscript_report_decision_packet(
        rows=rows,
        output_path=args.output,
        manifest_path=args.manifest,
        doc_path=args.doc,
        paper_path=args.paper,
        report_path=args.report,
        report_docx_path=args.report_docx,
        figure_manifest_path=args.figure_manifest,
        claim_alignment_manifest_path=args.claim_alignment_manifest,
        figure_table_review_manifest_path=args.figure_table_review_manifest,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write a non-approval worksheet for manuscript/report claim, "
            "figure/table, docx, and acceptance-boundary decisions."
        )
    )
    parser.add_argument("--paper", type=Path, default=DEFAULT_PAPER_DRAFT_PATH)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT_DRAFT_PATH)
    parser.add_argument(
        "--report-docx",
        type=Path,
        default=DEFAULT_REPORT_DOCX_PATH,
    )
    parser.add_argument(
        "--figure-manifest",
        type=Path,
        default=DEFAULT_FIGURE_TABLE_MANIFEST_PATH,
    )
    parser.add_argument(
        "--claim-alignment-manifest",
        type=Path,
        default=DEFAULT_CLAIM_ALIGNMENT_REVIEW_MANIFEST_PATH,
    )
    parser.add_argument(
        "--figure-table-review-manifest",
        type=Path,
        default=DEFAULT_FIGURE_TABLE_REVIEW_MANIFEST_PATH,
    )
    parser.add_argument(
        "--manuscript-acceptance",
        type=Path,
        default=DEFAULT_MANUSCRIPT_ACCEPTANCE_PATH,
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_MANUSCRIPT_REPORT_DECISION_PACKET_PATH,
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANUSCRIPT_REPORT_DECISION_MANIFEST_PATH,
    )
    parser.add_argument(
        "--doc",
        type=Path,
        default=DEFAULT_MANUSCRIPT_REPORT_DECISION_DOC_PATH,
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
