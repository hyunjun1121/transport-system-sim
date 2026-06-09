"""Write the static timetable segment-pair diagnostic artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.rail_static_timetable_segment_pair_diagnostic import (  # noqa: E402
    DEFAULT_DIAGNOSTIC_CSV_PATH,
    DEFAULT_DIAGNOSTIC_DOC_PATH,
    DEFAULT_DIAGNOSTIC_MANIFEST_PATH,
    DEFAULT_STATIC_TIMETABLE_SOURCE_PATH,
    write_static_timetable_segment_pair_diagnostic,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    manifest = write_static_timetable_segment_pair_diagnostic(
        source_path=args.source,
        output_path=args.output,
        manifest_path=args.manifest,
        doc_path=args.doc,
        assumed_transfer_buffer_min=args.assumed_transfer_buffer_min,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write a non-evidence static timetable segment-pair diagnostic. "
            "This does not write rail_service_evidence.csv."
        )
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_STATIC_TIMETABLE_SOURCE_PATH,
        help="Retained static timetable source CSV.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_DIAGNOSTIC_CSV_PATH,
        help="Diagnostic CSV output.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_DIAGNOSTIC_MANIFEST_PATH,
        help="Diagnostic manifest JSON output.",
    )
    parser.add_argument(
        "--doc",
        type=Path,
        default=DEFAULT_DIAGNOSTIC_DOC_PATH,
        help="Diagnostic Markdown output.",
    )
    parser.add_argument(
        "--assumed-transfer-buffer-min",
        type=float,
        default=5.0,
        help="Assumed minimum transfer buffer used only for diagnostic connection matching.",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
