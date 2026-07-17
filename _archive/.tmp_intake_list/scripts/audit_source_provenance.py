"""Audit the source provenance review packet without accepting it."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.source_provenance import (  # noqa: E402
    summarize_source_provenance_manifest,
)


def main() -> int:
    """Print source provenance diagnostics."""

    args = _parse_args()
    summary = summarize_source_provenance_manifest()
    print(json.dumps(summary, indent=2, sort_keys=True))
    if args.fail_on_blockers and summary["remaining_blockers"]:
        return 1
    return 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fail-on-blockers",
        action="store_true",
        help="Return exit code 1 when manifest schema or local artifact paths are invalid.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
