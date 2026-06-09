"""Write the current rail evidence review packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.rail_evidence import DEFAULT_RAIL_SERVICE_EVIDENCE_PATH  # noqa: E402
from src.realworld.rail_evidence_review_packet import (  # noqa: E402
    DEFAULT_RAIL_ASSUMPTIONS_PATH,
    DEFAULT_RAIL_EVIDENCE_REVIEW_MANIFEST_PATH,
    DEFAULT_RAIL_EVIDENCE_REVIEW_PACKET_PATH,
    build_rail_evidence_review_rows,
    write_rail_evidence_review_packet,
)
from src.realworld.rail_station_binding import (  # noqa: E402
    DEFAULT_RAIL_STATION_BINDING_PATH,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    rows = build_rail_evidence_review_rows(
        service_evidence_path=args.service_evidence,
        station_binding_path=args.station_bindings,
        assumptions_path=args.assumptions,
        required_points=tuple(args.required_points.split(",")),
    )
    manifest = write_rail_evidence_review_packet(
        rows=rows,
        output_path=args.output,
        manifest_path=args.manifest,
        service_evidence_path=args.service_evidence,
        station_binding_path=args.station_bindings,
        assumptions_path=args.assumptions,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write a conservative rail evidence review packet. The output is a "
            "review aid only, not rail-service calibration or route-use "
            "evidence."
        )
    )
    parser.add_argument(
        "--service-evidence",
        type=Path,
        default=DEFAULT_RAIL_SERVICE_EVIDENCE_PATH,
        help="Rail service evidence CSV path.",
    )
    parser.add_argument(
        "--station-bindings",
        type=Path,
        default=DEFAULT_RAIL_STATION_BINDING_PATH,
        help="Rail station binding CSV path.",
    )
    parser.add_argument(
        "--assumptions",
        type=Path,
        default=DEFAULT_RAIL_ASSUMPTIONS_PATH,
        help="Rail assumptions CSV path.",
    )
    parser.add_argument(
        "--required-points",
        default="S,R",
        help="Comma-separated required simulator rail point IDs.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_RAIL_EVIDENCE_REVIEW_PACKET_PATH,
        help="Rail evidence review CSV path.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_RAIL_EVIDENCE_REVIEW_MANIFEST_PATH,
        help="Rail evidence review manifest JSON path.",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
