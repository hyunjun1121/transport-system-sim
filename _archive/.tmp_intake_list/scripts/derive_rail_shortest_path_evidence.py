"""Derive rail travel-time evidence from a cached shortest-path CSV."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.realworld.rail_evidence import load_rail_service_evidence  # noqa: E402
from src.realworld.rail_shortest_path import (  # noqa: E402
    RailShortestPathEvidenceConfig,
    derive_rail_service_evidence_from_shortest_path,
    file_sha256,
    load_cached_shortest_path_records,
    write_rail_shortest_path_evidence,
)
from src.realworld.rail_station_binding import (  # noqa: E402
    DEFAULT_RAIL_STATION_BINDING_PATH,
    load_rail_station_bindings,
)


def main(argv: list[str] | None = None) -> int:
    """Run the cached shortest-path derivation command."""

    args = _parse_args(argv)
    input_path = Path(args.input)
    records = load_cached_shortest_path_records(input_path)
    station_bindings = load_rail_station_bindings(args.station_bindings)
    record = derive_rail_service_evidence_from_shortest_path(
        records,
        RailShortestPathEvidenceConfig(
            evidence_id=args.evidence_id,
            region_id=args.region_id,
            access_point=args.access_point,
            egress_point=args.egress_point,
            source_name=args.source_name,
            source_url_or_citation=args.source_url_or_citation,
            extraction_date=args.extraction_date,
            headway_min_proxy=args.headway_min_proxy,
            capacity_pax_per_train=args.capacity_pax_per_train,
            service_window=args.service_window,
            route_type=args.route_type,
            source_artifact_path=_display_path(input_path),
            source_artifact_sha256=file_sha256(input_path),
        ),
        station_bindings=station_bindings,
    )
    write_rail_shortest_path_evidence([record], args.output)
    load_rail_service_evidence(args.output)
    print(f"wrote {args.output}")
    print("source_status: cached_shortest_path_derived")
    print(
        "claim_scope: cached shortest-path-derived rail travel-time evidence; "
        "headway and capacity remain sensitivity-only; not operational forecast"
    )
    print(f"source_artifact_sha256: {file_sha256(input_path)}")
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Derive one rail-service evidence row from a cached station-to-"
            "station shortest-path CSV. This command does not call live APIs."
        )
    )
    parser.add_argument("--input", required=True, help="Cached shortest-path CSV path")
    parser.add_argument("--output", required=True, help="Output rail evidence CSV path")
    parser.add_argument("--evidence-id", required=True)
    parser.add_argument("--region-id", default="songpa_public_demo")
    parser.add_argument("--access-point", default="S")
    parser.add_argument("--egress-point", default="R")
    parser.add_argument("--source-name", required=True)
    parser.add_argument("--source-url-or-citation", required=True)
    parser.add_argument("--extraction-date", required=True)
    parser.add_argument("--headway-min-proxy", type=float, required=True)
    parser.add_argument("--capacity-pax-per-train", type=float, required=True)
    parser.add_argument("--service-window", required=True)
    parser.add_argument("--route-type", default="minimum_time")
    parser.add_argument(
        "--station-bindings",
        default=str(DEFAULT_RAIL_STATION_BINDING_PATH),
        help=(
            "Rail station-binding CSV used to verify shortest-path station "
            "codes against official point bindings"
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
