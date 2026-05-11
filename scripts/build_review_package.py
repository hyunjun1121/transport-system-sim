"""Build an expert-review ZIP from the review-package inventory."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.review_package_builder import build_review_package_zip  # noqa: E402


def main() -> int:
    """Build the review ZIP and print the build manifest."""

    args = _parse_args()
    summary = build_review_package_zip(
        output_zip_path=args.output,
        include_formal_targets=args.include_formal_targets,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    if args.fail_on_missing and summary["missing_file_count"] > 0:
        return 1
    return 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "review_packages" / "expert_review_package.zip",
        help="Output ZIP path. The existing user-supplied required_deliverables.zip is not overwritten by default.",
    )
    parser.add_argument(
        "--include-formal-targets",
        action="store_true",
        help="Include formal acceptance target files even if they are current blocker/template files.",
    )
    parser.add_argument(
        "--fail-on-missing",
        action="store_true",
        help="Return exit code 1 when inventory rows reference missing files.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
