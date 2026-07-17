"""Audit cached OSM road evidence by highway class without accepting it."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.road_evidence_diagnostics import (  # noqa: E402
    audit_cached_road_evidence_diagnostics,
)


def main() -> int:
    """Print a JSON road-class evidence diagnostic audit."""

    args = _parse_args()
    summary = (
        audit_cached_road_evidence_diagnostics(args.graphml)
        if args.graphml
        else audit_cached_road_evidence_diagnostics()
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    if args.fail_on_structural_blockers and summary["remaining_blockers"]:
        return 1
    return 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--graphml",
        default=None,
        help="Optional cached GraphML path. Defaults to data/cache/pilot_region_road.graphml.",
    )
    parser.add_argument(
        "--fail-on-structural-blockers",
        action="store_true",
        help=(
            "Return exit code 1 only when the graph is missing, empty, "
            "or has no routeable edges."
        ),
    )
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
