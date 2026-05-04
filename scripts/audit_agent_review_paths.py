"""Audit sub-agent review-record path hygiene."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.agent_review_path_audit import (  # noqa: E402
    write_agent_review_path_audit,
)


def main() -> int:
    """Write agent-review path audit artifacts and print the summary."""

    args = _parse_args()
    summary = write_agent_review_path_audit()
    print(json.dumps(summary, indent=2, sort_keys=True))
    if args.fail_on_missing and not summary["agent_review_paths_ready"]:
        return 1
    return 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fail-on-missing",
        action="store_true",
        help="Return exit code 1 if review records cite missing non-formal paths.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
