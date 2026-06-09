"""Write the dirty-worktree classification ledger."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.tracked_artifact_audit import (  # noqa: E402
    write_dirty_worktree_classification,
)


def main() -> int:
    """Write dirty-worktree classification artifacts and print the manifest."""

    args = _parse_args()
    summary = write_dirty_worktree_classification()
    print(json.dumps(summary, indent=2, sort_keys=True))
    if args.fail_on_blockers and not summary["new_generated_output_allowed"]:
        return 1
    return 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fail-on-blockers",
        action="store_true",
        help="Return exit code 1 when dirty paths block new generated-output work.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
