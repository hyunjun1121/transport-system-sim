"""Write the road-class override source-candidate review packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.road_override_audit import (  # noqa: E402
    DEFAULT_ROAD_CLASS_OVERRIDE_DRAFT_PATH,
)
from src.realworld.road_override_source_candidate import (  # noqa: E402
    DEFAULT_ROAD_OVERRIDE_SOURCE_CANDIDATE_DOC_PATH,
    DEFAULT_ROAD_OVERRIDE_SOURCE_CANDIDATE_MANIFEST_PATH,
    DEFAULT_ROAD_OVERRIDE_SOURCE_CANDIDATE_PATH,
    build_road_override_source_candidate_rows,
    write_road_override_source_candidate_packet,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    rows = build_road_override_source_candidate_rows(args.draft)
    manifest = write_road_override_source_candidate_packet(
        rows=rows,
        output_path=args.output,
        manifest_path=args.manifest,
        doc_path=args.doc,
        draft_path=args.draft,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write a non-formal road-class override source-candidate packet. "
            "This does not create data/parameters/road_class_overrides.csv."
        )
    )
    parser.add_argument(
        "--draft",
        type=Path,
        default=DEFAULT_ROAD_CLASS_OVERRIDE_DRAFT_PATH,
        help="Draft road-class override worksheet path.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_ROAD_OVERRIDE_SOURCE_CANDIDATE_PATH,
        help="Source-candidate CSV path.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_ROAD_OVERRIDE_SOURCE_CANDIDATE_MANIFEST_PATH,
        help="Source-candidate manifest path.",
    )
    parser.add_argument(
        "--doc",
        type=Path,
        default=DEFAULT_ROAD_OVERRIDE_SOURCE_CANDIDATE_DOC_PATH,
        help="Source-candidate Markdown path.",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
