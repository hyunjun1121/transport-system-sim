"""Audit local path references inside the expert-review ZIP."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.review_package_path_audit import (  # noqa: E402
    DEFAULT_REVIEW_PACKAGE_ZIP,
    write_review_package_path_audit,
)


def main() -> int:
    """Write review-package path audit artifacts and print the summary."""

    args = _parse_args()
    summary = write_review_package_path_audit(zip_path=args.zip)
    print(json.dumps(summary, indent=2, sort_keys=True))
    if args.fail_on_missing and not summary["review_package_paths_ready"]:
        return 1
    return 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--zip",
        type=Path,
        default=DEFAULT_REVIEW_PACKAGE_ZIP,
        help="Review ZIP path to audit.",
    )
    parser.add_argument(
        "--fail-on-missing",
        action="store_true",
        help="Return exit code 1 if any non-formal referenced package path is missing.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
