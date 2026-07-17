"""Write the current core-parameter evidence review packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.parameter_review_packet import (  # noqa: E402
    DEFAULT_PARAMETER_REVIEW_PACKET_MANIFEST_PATH,
    DEFAULT_PARAMETER_REVIEW_PACKET_PATH,
    build_parameter_review_rows,
    write_parameter_review_packet,
)
from src.realworld.parameters import DEFAULT_PARAMETER_DIR  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    rows = build_parameter_review_rows(parameter_dir=args.parameter_dir)
    manifest = write_parameter_review_packet(
        rows=rows,
        output_path=args.output,
        manifest_path=args.manifest,
        parameter_dir=args.parameter_dir,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write a conservative core-parameter evidence review packet. "
            "The output is a review aid only, not parameter acceptance."
        )
    )
    parser.add_argument(
        "--parameter-dir",
        type=Path,
        default=DEFAULT_PARAMETER_DIR,
        help="Directory containing shipped parameter evidence tables.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_PARAMETER_REVIEW_PACKET_PATH,
        help="Parameter review CSV path.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_PARAMETER_REVIEW_PACKET_MANIFEST_PATH,
        help="Parameter review manifest JSON path.",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
