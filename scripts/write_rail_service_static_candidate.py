"""Write the non-formal static rail-service candidate packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.rail_service_static_candidate import (  # noqa: E402
    DEFAULT_RAIL_STATIC_CANDIDATE_DOC_PATH,
    DEFAULT_RAIL_STATIC_CANDIDATE_MANIFEST_PATH,
    DEFAULT_RAIL_STATIC_CANDIDATE_PATH,
    DEFAULT_SEGMENT_PAIR_DIAGNOSTIC_PATH,
    DEFAULT_STATIC_TIMETABLE_CACHE_PATH,
    build_rail_static_candidate_rows,
    write_rail_static_candidate_packet,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    rows = build_rail_static_candidate_rows(
        timetable_cache_path=args.timetable_cache,
        segment_pair_diagnostic_path=args.segment_pair_diagnostic,
        current_capacity_pax_per_train=args.capacity_pax_per_train,
    )
    manifest = write_rail_static_candidate_packet(
        rows=rows,
        output_path=args.output,
        manifest_path=args.manifest,
        doc_path=args.doc,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write a non-formal static rail-service candidate. This does not "
            "modify data/parameters/rail_service_evidence.csv."
        )
    )
    parser.add_argument(
        "--timetable-cache",
        type=Path,
        default=DEFAULT_STATIC_TIMETABLE_CACHE_PATH,
        help="Normalized static timetable cache CSV.",
    )
    parser.add_argument(
        "--segment-pair-diagnostic",
        type=Path,
        default=DEFAULT_SEGMENT_PAIR_DIAGNOSTIC_PATH,
        help="Static timetable segment-pair diagnostic CSV.",
    )
    parser.add_argument(
        "--capacity-pax-per-train",
        type=float,
        default=500.0,
        help="Current sensitivity-only capacity candidate.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_RAIL_STATIC_CANDIDATE_PATH,
        help="Candidate CSV output path.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_RAIL_STATIC_CANDIDATE_MANIFEST_PATH,
        help="Candidate manifest JSON output path.",
    )
    parser.add_argument(
        "--doc",
        type=Path,
        default=DEFAULT_RAIL_STATIC_CANDIDATE_DOC_PATH,
        help="Candidate Markdown output path.",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
