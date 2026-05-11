"""Run bounded clean-checkout reproducibility smoke evidence.

This command clones the committed source tree and runs the existing smoke
ladder inside that clone. It writes non-acceptance evidence only.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.clean_checkout_smoke import run_clean_checkout_smoke  # noqa: E402


def main() -> int:
    """Run the clean-checkout smoke and print the manifest."""

    args = _parse_args()
    manifest = run_clean_checkout_smoke(
        source_repo=args.source_repo,
        keep_checkout=args.keep_checkout,
        checkout_parent=args.checkout_parent,
        install_dependencies=args.install_dependencies,
        artifact_regeneration=args.artifact_regeneration,
        timeout_sec=args.timeout_sec,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0 if manifest["smoke_passed"] else 1


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-repo",
        type=Path,
        default=ROOT,
        help="Repository to clone. Defaults to the current project root.",
    )
    parser.add_argument(
        "--checkout-parent",
        type=Path,
        default=None,
        help="Optional parent directory for a named checkout directory.",
    )
    parser.add_argument(
        "--keep-checkout",
        action="store_true",
        help="Retain the generated checkout directory for manual inspection.",
    )
    parser.add_argument(
        "--install-dependencies",
        action="store_true",
        help=(
            "Create a fresh venv in the checkout, install requirements.txt, "
            "and run the bounded smoke there."
        ),
    )
    parser.add_argument(
        "--artifact-regeneration",
        action="store_true",
        help=(
            "After the bounded smoke passes, regenerate bounded review and "
            "audit artifacts inside the clean checkout."
        ),
    )
    parser.add_argument(
        "--timeout-sec",
        type=int,
        default=1800,
        help="Timeout for clone and smoke subprocesses.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
