"""Write the rail source-decision recommendation packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.rail_source_decision_packet import (  # noqa: E402
    DEFAULT_RAIL_SOURCE_DECISION_MANIFEST_PATH,
    DEFAULT_RAIL_SOURCE_DECISION_PACKET_PATH,
)
from src.realworld.rail_source_decision_recommendation_packet import (  # noqa: E402
    DEFAULT_RAIL_SOURCE_DECISION_RECOMMENDATION_DOC_PATH,
    DEFAULT_RAIL_SOURCE_DECISION_RECOMMENDATION_MANIFEST_PATH,
    DEFAULT_RAIL_SOURCE_DECISION_RECOMMENDATION_PACKET_PATH,
    build_rail_source_decision_recommendation_rows,
    write_rail_source_decision_recommendation_packet,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    rows = build_rail_source_decision_recommendation_rows(
        decision_packet_path=args.decision_packet,
    )
    manifest = write_rail_source_decision_recommendation_packet(
        rows=rows,
        output_path=args.output,
        manifest_path=args.manifest,
        doc_path=args.doc,
        decision_packet_path=args.decision_packet,
        decision_manifest_path=args.decision_manifest,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write rail source-decision recommendations. The output is "
            "review support only, not an action ledger, not rail evidence, "
            "not publication readiness, and not formal acceptance."
        )
    )
    parser.add_argument(
        "--decision-packet",
        type=Path,
        default=DEFAULT_RAIL_SOURCE_DECISION_PACKET_PATH,
    )
    parser.add_argument(
        "--decision-manifest",
        type=Path,
        default=DEFAULT_RAIL_SOURCE_DECISION_MANIFEST_PATH,
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_RAIL_SOURCE_DECISION_RECOMMENDATION_PACKET_PATH,
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_RAIL_SOURCE_DECISION_RECOMMENDATION_MANIFEST_PATH,
    )
    parser.add_argument(
        "--doc",
        type=Path,
        default=DEFAULT_RAIL_SOURCE_DECISION_RECOMMENDATION_DOC_PATH,
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
