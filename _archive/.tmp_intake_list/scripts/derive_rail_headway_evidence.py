"""Derive rail headway evidence from a cached station-event timetable CSV."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.rail_evidence import load_rail_service_evidence  # noqa: E402
from src.realworld.rail_station_binding import (  # noqa: E402
    DEFAULT_RAIL_STATION_BINDING_PATH,
    load_rail_station_bindings,
)
from src.realworld.rail_timetable import (  # noqa: E402
    RailHeadwayEvidenceConfig,
    derive_rail_headway_evidence_from_timetable,
    file_sha256,
    load_cached_timetable_events,
    write_rail_service_evidence,
)


def main(argv: list[str] | None = None) -> int:
    """Run the cached-headway derivation command."""

    args = _parse_args(argv)
    events = load_cached_timetable_events(args.input)
    station_bindings = load_rail_station_bindings(args.station_bindings)
    input_path = Path(args.input)
    record = derive_rail_headway_evidence_from_timetable(
        events,
        RailHeadwayEvidenceConfig(
            evidence_id=args.evidence_id,
            region_id=args.region_id,
            access_point=args.access_point,
            egress_point=args.egress_point,
            egress_station_name=args.egress_station_name,
            source_name=args.source_name,
            source_url_or_citation=args.source_url_or_citation,
            extraction_date=args.extraction_date,
            travel_time_min_proxy=args.travel_time_min_proxy,
            capacity_pax_per_train=args.capacity_pax_per_train,
            service_window=args.service_window,
            direction=args.direction,
            service_day=args.service_day,
            source_artifact_path=_display_path(input_path),
            source_artifact_sha256=file_sha256(input_path),
        ),
        station_bindings=station_bindings,
    )
    write_rail_service_evidence([record], args.output)
    # Re-load through the production validator so this script fails on schema drift.
    load_rail_service_evidence(args.output)
    print(f"wrote {args.output}")
    print("source_status: cached_timetable_derived")
    print("derived_fields: headway")
    print(
        "claim_scope: cached timetable-derived headway evidence only; "
        "travel time and capacity remain separate assumptions or sensitivity values"
    )
    print(f"source_artifact_sha256: {file_sha256(input_path)}")
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Derive one headway-only rail-service evidence row from a cached "
            "station-event timetable CSV. This command does not call live APIs."
        )
    )
    parser.add_argument("--input", required=True, help="Cached timetable CSV path")
    parser.add_argument("--output", required=True, help="Output rail evidence CSV path")
    parser.add_argument("--evidence-id", required=True)
    parser.add_argument("--region-id", default="songpa_public_demo")
    parser.add_argument("--access-point", default="S")
    parser.add_argument("--egress-point", default="R")
    parser.add_argument("--egress-station-name", required=True)
    parser.add_argument("--source-name", required=True)
    parser.add_argument("--source-url-or-citation", required=True)
    parser.add_argument("--extraction-date", required=True)
    parser.add_argument("--travel-time-min-proxy", type=float, required=True)
    parser.add_argument("--capacity-pax-per-train", type=float, required=True)
    parser.add_argument("--service-window", required=True)
    parser.add_argument("--direction", default="")
    parser.add_argument("--service-day", default="")
    parser.add_argument(
        "--station-bindings",
        default=str(DEFAULT_RAIL_STATION_BINDING_PATH),
        help=(
            "Rail station-binding CSV used to verify timetable station codes "
            "against official access-point bindings"
        ),
    )
    return parser.parse_args(argv)


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
