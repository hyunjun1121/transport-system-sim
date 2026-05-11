"""Write the external-review package inventory."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.review_package_inventory import (  # noqa: E402
    write_review_package_inventory,
)


def main() -> int:
    """Write review package inventory artifacts and print the manifest."""

    args = _parse_args()
    summary = write_review_package_inventory()
    print(json.dumps(summary, indent=2, sort_keys=True))
    if args.fail_on_missing_required and summary["missing_required_group_count"] > 0:
        return 1
    return 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fail-on-missing-required",
        action="store_true",
        help="Return exit code 1 when a required package group is missing.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
