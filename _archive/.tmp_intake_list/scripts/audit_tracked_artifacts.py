"""Write the clean-checkout tracked-artifact packaging audit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.tracked_artifact_audit import write_tracked_artifact_audit  # noqa: E402


def main() -> int:
    """Write tracked-artifact audit artifacts and print the manifest."""

    args = _parse_args()
    summary = write_tracked_artifact_audit()
    print(json.dumps(summary, indent=2, sort_keys=True))
    if args.fail_on_blockers and summary["blocking_change_count"] > 0:
        return 1
    return 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fail-on-blockers",
        action="store_true",
        help="Return exit code 1 when changed artifacts would be missing from a clean checkout.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
