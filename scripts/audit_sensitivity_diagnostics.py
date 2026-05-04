"""Audit scaffold Morris sensitivity output diagnostics."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.sensitivity_diagnostics import (  # noqa: E402
    audit_morris_sensitivity_diagnostics,
)


def main() -> int:
    """Print a JSON Morris sensitivity diagnostic audit."""

    args = _parse_args()
    summary = audit_morris_sensitivity_diagnostics()
    print(json.dumps(summary, indent=2, sort_keys=True))
    if args.fail_on_structural_blockers and summary["remaining_blockers"]:
        return 1
    return 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fail-on-structural-blockers",
        action="store_true",
        help="Return exit code 1 only for missing files, bad schema, or count mismatches.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
