"""Write the current rail timing source-request packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.rail_evidence_review_packet import DEFAULT_RAIL_ASSUMPTIONS_PATH  # noqa: E402
from src.realworld.rail_station_binding import (  # noqa: E402
    DEFAULT_RAIL_STATION_BINDING_PATH,
)
from src.realworld.rail_timing_request_packet import (  # noqa: E402
    DEFAULT_RAIL_CACHE_PREFIX,
    DEFAULT_RAIL_TIMING_SOURCE_REQUEST_MANIFEST_PATH,
    DEFAULT_RAIL_TIMING_SOURCE_REQUEST_PACKET_PATH,
    build_rail_timing_source_request_rows,
    write_rail_timing_source_request_packet,
)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""

    args = _parse_args(argv)
    rows = build_rail_timing_source_request_rows(
        station_binding_path=args.station_bindings,
        assumptions_path=args.assumptions,
        cache_prefix=args.cache_prefix,
    )
    manifest = write_rail_timing_source_request_packet(
        rows=rows,
        output_path=args.output,
        manifest_path=args.manifest,
        station_binding_path=args.station_bindings,
        assumptions_path=args.assumptions,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Write the rail timing source-request worksheet. The output names "
            "required source inputs and commands; it is not timing evidence."
        )
    )
    parser.add_argument(
        "--cache-prefix",
        default=DEFAULT_RAIL_CACHE_PREFIX,
        help=(
            "Prefix for suggested rail cache files in generated commands. "
            "Defaults to the current pilot prefix."
        ),
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
        "--output",
        type=Path,
        default=DEFAULT_RAIL_TIMING_SOURCE_REQUEST_PACKET_PATH,
        help="Rail timing source-request CSV path.",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_RAIL_TIMING_SOURCE_REQUEST_MANIFEST_PATH,
        help="Rail timing source-request manifest JSON path.",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
