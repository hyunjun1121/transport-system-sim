"""Audit pilot replication and paired-delta statistics adequacy."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.replication_adequacy_audit import (  # noqa: E402
    write_replication_adequacy_audit,
)


def main() -> int:
    """Write replication adequacy audit artifacts and print the manifest."""

    args = _parse_args()
    summary = write_replication_adequacy_audit(
        minimum_seed_count=args.minimum_seed_count,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    if args.fail_on_blockers and summary["blocking_check_count"] > 0:
        return 1
    return 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--minimum-seed-count",
        type=int,
        default=30,
        help="Minimum structural seed count before human adequacy review.",
    )
    parser.add_argument(
        "--fail-on-blockers",
        action="store_true",
        help="Return exit code 1 when structural replication checks are blocked.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
