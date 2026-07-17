"""Run bounded current-worktree reproducibility smoke checks.

This command writes smoke evidence only. It does not perform clean-checkout
reproduction and does not create formal reproducibility acceptance.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.reproducibility_smoke import (  # noqa: E402
    CLEAN_CHECKOUT_MINIMAL_SMOKE_COMMANDS,
    DEFAULT_SMOKE_COMMANDS,
    run_reproducibility_smoke,
)


def main() -> int:
    """Run the smoke command ladder and print the manifest."""

    args = _parse_args()
    commands = (
        CLEAN_CHECKOUT_MINIMAL_SMOKE_COMMANDS
        if args.profile == "clean-checkout-minimal"
        else DEFAULT_SMOKE_COMMANDS
    )
    manifest = run_reproducibility_smoke(commands=commands)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0 if manifest["smoke_passed"] else 1


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--profile",
        choices=("default", "clean-checkout-minimal"),
        default="default",
        help="Smoke command profile to execute.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
