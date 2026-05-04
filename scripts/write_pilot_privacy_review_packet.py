"""Write the current pilot-region privacy review packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.pilot_privacy_review_packet import (  # noqa: E402
    DEFAULT_PILOT_DATA_CARD_PATH,
    DEFAULT_PILOT_PRIVACY_REVIEW_DOC_PATH,
    DEFAULT_PILOT_PRIVACY_REVIEW_MANIFEST_PATH,
    DEFAULT_PILOT_PRIVACY_REVIEW_PACKET_PATH,
    DEFAULT_PILOT_REGION_PATH,
    build_pilot_privacy_review_rows,
    write_pilot_privacy_review_packet,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    rows = build_pilot_privacy_review_rows(
        region_path=args.region,
        data_card_path=args.data_card,
    )
    manifest = write_pilot_privacy_review_packet(
        rows=rows,
        output_path=args.output,
        manifest_path=args.manifest,
        doc_path=args.doc,
        region_path=args.region,
        data_card_path=args.data_card,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write pilot-region privacy review rows. The output is a reviewer "
            "packet and does not create pilot acceptance."
        )
    )
    parser.add_argument(
        "--region",
        type=Path,
        default=DEFAULT_PILOT_REGION_PATH,
        help="Pilot region YAML path.",
    )
    parser.add_argument(
        "--data-card",
        type=Path,
        default=DEFAULT_PILOT_DATA_CARD_PATH,
        help="Pilot region data-card Markdown path.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_PILOT_PRIVACY_REVIEW_PACKET_PATH,
        help="Pilot privacy review CSV path.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_PILOT_PRIVACY_REVIEW_MANIFEST_PATH,
        help="Pilot privacy review manifest JSON path.",
    )
    parser.add_argument(
        "--doc",
        type=Path,
        default=DEFAULT_PILOT_PRIVACY_REVIEW_DOC_PATH,
        help="Pilot privacy review Markdown path.",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
