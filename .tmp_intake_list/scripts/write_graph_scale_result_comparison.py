"""Write current-vs-multi-corridor full-profile graph-scale result deltas."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.graph_scale_result_comparison import (  # noqa: E402
    DEFAULT_CANDIDATE_SUMMARY_PATH,
    DEFAULT_CURRENT_SUMMARY_PATH,
    DEFAULT_RESULT_COMPARISON_MANIFEST_PATH,
    DEFAULT_RESULT_COMPARISON_PATH,
    build_graph_scale_result_comparison_rows,
    write_graph_scale_result_comparison,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    rows = build_graph_scale_result_comparison_rows(
        current_summary_path=args.current_summary,
        candidate_summary_path=args.candidate_summary,
    )
    manifest = write_graph_scale_result_comparison(
        rows=rows,
        output_path=args.output,
        manifest_path=args.manifest,
        current_summary_path=args.current_summary,
        candidate_summary_path=args.candidate_summary,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write metric-level deltas between the current full pilot and the "
            "full-profile multi-corridor candidate. This is review support "
            "only, not graph-scale acceptance."
        )
    )
    parser.add_argument(
        "--current-summary",
        type=Path,
        default=DEFAULT_CURRENT_SUMMARY_PATH,
        help="Current reduced-corridor full-pilot summary CSV.",
    )
    parser.add_argument(
        "--candidate-summary",
        type=Path,
        default=DEFAULT_CANDIDATE_SUMMARY_PATH,
        help="Full-profile multi-corridor candidate summary CSV.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_RESULT_COMPARISON_PATH,
        help="Output comparison CSV path.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_RESULT_COMPARISON_MANIFEST_PATH,
        help="Output manifest JSON path.",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
