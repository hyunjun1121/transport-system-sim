"""Run bounded current-worktree reproducibility smoke checks.

This command writes smoke evidence only. It does not perform clean-checkout
reproduction and does not create formal reproducibility acceptance.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.reproducibility_smoke import run_reproducibility_smoke  # noqa: E402


def main() -> int:
    """Run the smoke command ladder and print the manifest."""

    manifest = run_reproducibility_smoke()
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0 if manifest["smoke_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
