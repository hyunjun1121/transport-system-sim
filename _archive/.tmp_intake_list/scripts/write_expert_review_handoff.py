"""Write the external expert-review handoff sidecar."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.review_package_handoff import (  # noqa: E402
    DEFAULT_EXPERT_REVIEW_HANDOFF_DOC,
    DEFAULT_EXPERT_REVIEW_HANDOFF_MANIFEST,
    write_expert_review_handoff,
)


def main() -> int:
    """Write the handoff sidecar and print its summary."""

    args = _parse_args()
    summary = write_expert_review_handoff(
        output_path=args.output,
        manifest_path=args.manifest_output,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    if args.fail_on_zip_mismatch and not summary["mirror_zip"]["matches_zip"]:
        return 1
    return 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_EXPERT_REVIEW_HANDOFF_DOC,
        help="Output Markdown handoff sidecar path.",
    )
    parser.add_argument(
        "--manifest-output",
        type=Path,
        default=DEFAULT_EXPERT_REVIEW_HANDOFF_MANIFEST,
        help="Output JSON handoff sidecar path.",
    )
    parser.add_argument(
        "--fail-on-zip-mismatch",
        action="store_true",
        help="Return exit code 1 when the mirrored ZIP hash differs from required_deliverables.zip.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    raise SystemExit(main())
