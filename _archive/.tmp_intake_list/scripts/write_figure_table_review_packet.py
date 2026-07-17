"""Write the figure/table review packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.figure_table_review_packet import (  # noqa: E402
    DEFAULT_FIGURE_TABLE_MANIFEST_PATH,
    DEFAULT_FIGURE_TABLE_REVIEW_DOC_PATH,
    DEFAULT_FIGURE_TABLE_REVIEW_MANIFEST_PATH,
    DEFAULT_FIGURE_TABLE_REVIEW_PACKET_PATH,
    build_figure_table_review_rows,
    write_figure_table_review_packet,
)
from src.realworld.manuscript_acceptance import (  # noqa: E402
    DEFAULT_MANUSCRIPT_ACCEPTANCE_PATH,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    rows = build_figure_table_review_rows(
        figure_manifest_path=args.figure_manifest,
        manuscript_acceptance_path=args.manuscript_acceptance,
    )
    manifest = write_figure_table_review_packet(
        rows=rows,
        output_path=args.output,
        manifest_path=args.manifest,
        doc_path=args.doc,
        figure_manifest_path=args.figure_manifest,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write a non-approval worksheet for figure/table artifact, "
            "caption, graph-scope, and manuscript-acceptance review."
        )
    )
    parser.add_argument(
        "--figure-manifest",
        type=Path,
        default=DEFAULT_FIGURE_TABLE_MANIFEST_PATH,
    )
    parser.add_argument(
        "--manuscript-acceptance",
        type=Path,
        default=DEFAULT_MANUSCRIPT_ACCEPTANCE_PATH,
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_FIGURE_TABLE_REVIEW_PACKET_PATH,
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_FIGURE_TABLE_REVIEW_MANIFEST_PATH,
    )
    parser.add_argument(
        "--doc",
        type=Path,
        default=DEFAULT_FIGURE_TABLE_REVIEW_DOC_PATH,
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
