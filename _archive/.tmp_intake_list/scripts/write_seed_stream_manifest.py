"""Write the pilot experiment seed-stream manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.seed_stream_manifest import write_seed_stream_manifest  # noqa: E402


def main() -> int:
    """Write seed-stream review artifacts and print the manifest."""

    args = _parse_args()
    manifest = write_seed_stream_manifest()
    print(json.dumps(manifest, indent=2, sort_keys=True))
    if args.fail_on_blockers and manifest["blocking_check_count"] > 0:
        return 1
    return 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fail-on-blockers",
        action="store_true",
        help="Return exit code 1 when seed-stream marker checks are blocked.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
