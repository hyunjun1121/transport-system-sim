"""Write the current sensitivity diagnostics review packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.sensitivity import (  # noqa: E402
    DEFAULT_MORRIS_MANIFEST_PATH,
    DEFAULT_MORRIS_SUMMARY_PATH,
)
from src.realworld.sensitivity_review_packet import (  # noqa: E402
    DEFAULT_SENSITIVITY_REVIEW_MANIFEST_PATH,
    DEFAULT_SENSITIVITY_REVIEW_PACKET_PATH,
    build_sensitivity_review_rows,
    write_sensitivity_review_packet,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    rows = build_sensitivity_review_rows(
        summary_path=args.summary,
        morris_manifest_path=args.morris_manifest,
    )
    manifest = write_sensitivity_review_packet(
        rows=rows,
        output_path=args.output,
        manifest_path=args.manifest,
        summary_path=args.summary,
        morris_manifest_path=args.morris_manifest,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write a conservative sensitivity review packet from current Morris "
            "diagnostics. The output is a review aid only, not sensitivity "
            "acceptance or calibrated evidence."
        )
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=DEFAULT_MORRIS_SUMMARY_PATH,
        help="Morris summary CSV path.",
    )
    parser.add_argument(
        "--morris-manifest",
        type=Path,
        default=DEFAULT_MORRIS_MANIFEST_PATH,
        help="Morris manifest JSON path.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_SENSITIVITY_REVIEW_PACKET_PATH,
        help="Sensitivity review packet CSV path.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_SENSITIVITY_REVIEW_MANIFEST_PATH,
        help="Sensitivity review manifest JSON path.",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
