"""Audit whether current evidence supports final-study publication claims."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.publication_readiness import audit_publication_readiness  # noqa: E402


def main() -> int:
    """Print a JSON readiness audit and optionally fail on blockers."""

    args = _parse_args()
    summary = audit_publication_readiness()
    print(json.dumps(summary, indent=2, sort_keys=True))
    if args.fail_on_blockers and not summary["publication_ready"]:
        return 1
    return 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fail-on-blockers",
        action="store_true",
        help="Return exit code 1 when final-study publication gates are blocked.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
